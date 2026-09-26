"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const account = {connected:false, scopes:[], audited:false};
  let mediaId = null;
  let jobId = null;
  let idempotencyKey = null;
  let sending = false;
  const labels = {
    PUBLIC_TO_EVERYONE:"Everyone", MUTUAL_FOLLOW_FRIENDS:"Friends (mutual follows)",
    FOLLOWER_OF_CREATOR:"Followers", SELF_ONLY:"Only me"
  };
  const text = (id,message) => {
    const element = $(id);
    if (element) element.textContent = message;
  };
  function csrf() {
    const item = document.cookie.split("; ").find(v => v.startsWith("zttato_csrf="));
    if (!item) throw new Error("Session expired. Reload the dashboard.");
    return decodeURIComponent(item.slice("zttato_csrf=".length));
  }
  async function api(path,options={}) {
    const opts={credentials:"same-origin",...options};
    if (opts.method && opts.method !== "GET") {
      opts.headers={...opts.headers,"X-CSRF-Token":csrf()};
    }
    const response=await fetch(path,opts);
    if (!response.ok) {
      let reason="Request failed ("+response.status+")";
      try {const data=await response.json(); reason=data.detail||reason;} catch (_) {}
      throw new Error(typeof reason==="string"?reason:"Request rejected.");
    }
    return response.json();
  }
  function report(message,isError=false) {
    text("status",message);
    $("status").classList.toggle("error",isError);
  }
  function mode() {return $("mode-direct")?.checked?"direct":"draft";}
  function review() {
    $("direct-options")?.classList.toggle("hidden",mode()!=="direct");
    const ready=Boolean(mediaId)&&Boolean($("consent")?.checked)&&!sending;
    const publish=$("publish");
    if (publish) {
      publish.disabled=!ready || (mode()==="direct" &&
        (!$("privacy")?.value || !account.scopes.includes("video.publish") ||
         Boolean($("mode-direct")?.disabled)));
    }
    text("summary",(mediaId?"A video is ready. ":"Upload an MP4 first. ")
       +(mode()==="draft"?"The video goes to your TikTok inbox, where you finish editing and posting."
       :"Direct Post will use the current TikTok visibility setting and any checked disclosures.")
       +" No transfer occurs until you confirm.");
  }
  function setCreatorFlag(id,disabled) {
    const control=$(id);
    if (!control) throw new Error("Dashboard UI version mismatch; refresh this page.");
    control.checked=Boolean(disabled);
    control.disabled=Boolean(disabled);
  }
  async function loadProfile() {
    const card=$("profile");
    const avatar=$("profile-avatar");
    if (!card) {
      text("connection-details","Dashboard UI version mismatch. Refresh to load your TikTok profile.");
      return;
    }
    card.classList.remove("hidden");
    text("profile-name","Loading TikTok profile…");
    if (!account.scopes.includes("user.info.basic")) {
      text("profile-name","TikTok profile unavailable");
      text("profile-message","Reconnect TikTok and grant user.info.basic.");
      return;
    }
    try {
      const profile=await api("/api/profile");
      text("profile-name",profile.display_name||"TikTok creator");
      text("profile-message","Basic profile retrieved from your authorized TikTok account.");
      if (avatar && profile.avatar_url) {
        avatar.onerror=()=>{
          avatar.classList.add("hidden");
          avatar.removeAttribute("src");
        };
        avatar.src=profile.avatar_url;
        avatar.classList.remove("hidden");
      }
    } catch(err) {
      text("profile-name","TikTok profile unavailable");
      text("profile-message",err.message+" You can retry by refreshing the dashboard.");
    }
  }
  async function loadCreator() {
    if (!account.scopes.includes("video.publish")) {
      $("mode-direct").disabled=true;
      text("creator-message","Direct Post requires the video.publish scope. Reconnect TikTok with this permission.");
      review();return;
    }
    try {
      const info=await api("/api/creator-info");
      const select=$("privacy"); select.replaceChildren();
      const choices=info.privacy_level_options.filter(value=>account.audited || value==="SELF_ONLY");
      for (const value of choices) {
        const option=document.createElement("option");
        option.value=value;option.textContent=labels[value]||value;
        select.append(option);
      }
      select.disabled=choices.length===0;
      setCreatorFlag("disable-comment",info.comment_disabled);
      setCreatorFlag("disable-duet",info.duet_disabled);
      setCreatorFlag("disable-stitch",info.stitch_disabled);
      text("creator-message","Connected: "+(info.nickname||info.username||"TikTok creator")
          +(account.audited?".":" · Unaudited app: Direct Post is limited to Only me.")
          +(info.max_video_post_duration_sec?" Max video duration: "+info.max_video_post_duration_sec+" seconds.":""));
      if (!choices.length) $("mode-direct").disabled=true;
    } catch(err) {
      if ($("mode-direct")) $("mode-direct").disabled=true;
      text("creator-message","Creator options unavailable: "+err.message);
    }
    review();
  }
  async function boot() {
    try {
      const data=await api("/api/session");
      Object.assign(account,data);
      text("connection",data.connected?"Your TikTok account is connected.":"Connect your TikTok account to start.");
      text("connection-details",data.connected?"Granted scopes: "+data.scopes.join(", "):"Authorization uses the official TikTok consent page.");
      $("connect").classList.toggle("hidden",data.connected);
      $("disconnect").classList.toggle("hidden",!data.connected);
      $("editor")?.classList.toggle("hidden",!data.connected);
      $("profile")?.classList.toggle("hidden",!data.connected);
      if (data.connected) {
        $("mode-draft").disabled=!data.scopes.includes("video.upload");
        $("mode-direct").disabled=!data.scopes.includes("video.publish");
        if ($("mode-draft").disabled&&!$("mode-direct").disabled) $("mode-direct").checked=true;
        await Promise.all([loadProfile(),loadCreator()]);
      }
    } catch(err) {text("connection",err.message);}
    review();
  }
  $("file").addEventListener("change",()=>{
    mediaId=null;jobId=null;idempotencyKey=null;
    $("refresh-status").disabled=true;
    $("upload").disabled=!$("file").files.length;
    text("media-result","");review();
  });
  $("upload").addEventListener("click",async()=>{
    const file=$("file").files[0];
    if(!file)return;
    if(file.size<12 || file.size>64*1024*1024){text("media-result","The video must be an MP4 under 64 MiB.");return;}
    $("upload").disabled=true;
    text("media-result","Uploading to your zTTato workspace…");
    try {
      const form=new FormData();form.append("file",file,file.name);
      const asset=await api("/api/media",{method:"POST",body:form});
      mediaId=asset.media_id;
      text("media-result",asset.filename+" · "+(asset.size/1048576).toFixed(2)+" MiB is ready.");
    }catch(err){text("media-result",err.message);}
    $("upload").disabled=false;review();
  });
  for(const id of ["mode-draft","mode-direct","privacy","consent"])$(id).addEventListener("change",()=>{
    if(id.startsWith("mode")) idempotencyKey=null;
    review();
  });
  $("publish").addEventListener("click",async()=>{
    if(sending||!mediaId||!$("consent").checked)return;
    if(!idempotencyKey)idempotencyKey=crypto.randomUUID();
    sending=true;review();report("Sending your confirmed request to TikTok…");
    const payload={
      media_id:mediaId,mode:mode(),idempotency_key:idempotencyKey,
      caption:$("caption").value,consent:true,
      privacy:mode()==="direct"?$("privacy").value:null,
      disable_comment:$("disable-comment").checked,
      disable_duet:$("disable-duet").checked,
      disable_stitch:$("disable-stitch").checked,
      brand_organic_toggle:$("own-brand").checked,
      brand_content_toggle:$("paid-brand").checked,
      is_aigc:$("ai-content").checked
    };
    try {
      const job=await api("/api/publish",{method:"POST",
        headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
      jobId=job.job_id;$("refresh-status").disabled=false;
      report(job.status+" · "+(job.note||"Check status for updates.")+(job.idempotent_replay?" (same request, not duplicated)":""));
    }catch(err){report("Request not confirmed: "+err.message+". If the result is uncertain, retry with the same request key or contact support.",true);}
    sending=false;review();
  });
  $("refresh-status").addEventListener("click",async()=>{
    if(!jobId)return;
    $("refresh-status").disabled=true;
    try {
      const result=await api("/api/jobs/"+encodeURIComponent(jobId));
      report(result.status+(result.fail_reason?" · "+result.fail_reason:""));
    }catch(err){report(err.message,true);}
    $("refresh-status").disabled=false;
  });
  $("disconnect").addEventListener("click",async()=>{
    if(!confirm("Disconnect TikTok from zTTato?"))return;
    try{await api("/api/disconnect",{method:"POST"});location.reload();}
    catch(err){report(err.message,true);}
  });
  $("delete-data").addEventListener("click",async()=>{
    if(!confirm("Permanently delete your local zTTato account, publishing records and uploaded files?"))return;
    try{await api("/api/my-data",{method:"DELETE"});location.href="/";}
    catch(err){report(err.message,true);}
  });
  boot();
})();
