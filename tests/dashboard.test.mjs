import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { runInNewContext } from "node:vm";

const html = readFileSync(new URL("../web/dashboard.html", import.meta.url), "utf8");
const javascript = readFileSync(new URL("../web/dashboard.js", import.meta.url), "utf8");

function dashboard({ missing = [] } = {}) {
  const ids = [...html.matchAll(/id="([^"]+)"/g)].map((match) => match[1]);
  const elements = new Map();
  for (const id of ids) {
    if (missing.includes(id)) continue;
    const classes = new Set();
    elements.set(id, {
      id,
      value: "",
      checked: false,
      disabled: false,
      textContent: "",
      files: [],
      classList: {
        add(name) { classes.add(name); },
        remove(name) { classes.delete(name); },
        toggle(name, force) {
          if (force ?? !classes.has(name)) classes.add(name);
          else classes.delete(name);
        },
        contains(name) { return classes.has(name); },
      },
      addEventListener() {},
      replaceChildren() { this.options = []; },
      append(item) { this.options = [...(this.options || []), item]; },
      removeAttribute(name) { delete this[name]; },
    });
  }
  const requests = [];
  const responses = {
    "/api/session": {
      connected: true,
      scopes: ["user.info.basic", "video.upload", "video.publish"],
      audited: false,
    },
    "/api/profile": {
      display_name: "Fixture Creator",
      avatar_url: "https://p16-sign.tiktokcdn-us.com/fixture.jpeg",
    },
    "/api/creator-info": {
      nickname: "Fixture Creator",
      username: "fixture_creator",
      privacy_level_options: ["SELF_ONLY"],
      comment_disabled: false,
      duet_disabled: false,
      stitch_disabled: false,
    },
  };
  const fetch = async (url) => {
    requests.push(url);
    if (!(url in responses)) throw new Error(`Unexpected request: ${url}`);
    return { ok: true, json: async () => responses[url] };
  };
  const document = {
    cookie: "zttato_csrf=fixture-csrf",
    getElementById: (id) => elements.get(id) || null,
    createElement: (tag) => ({ tag, textContent: "", value: "" }),
  };
  runInNewContext(javascript, {
    document, fetch, decodeURIComponent,
    confirm: () => false, crypto: { randomUUID: () => "fixture-uuid" },
    location: { reload() {}, href: "" },
  }, { filename: "dashboard.js" });
  return { elements, requests };
}

async function flush() {
  await new Promise((resolve) => setImmediate(resolve));
}

test("authorized basic profile renders independently from creator posting options", async () => {
  const { elements, requests } = dashboard();
  await flush();
  assert.equal(elements.get("connection").textContent, "Your TikTok account is connected.");
  assert.equal(elements.get("profile-name").textContent, "Fixture Creator");
  assert.equal(elements.get("profile-avatar").src, "https://p16-sign.tiktokcdn-us.com/fixture.jpeg");
  assert.ok(requests.includes("/api/profile"));
  assert.ok(requests.includes("/api/creator-info"));
});

test("missing optional interaction control fails closed without hiding connected profile", async () => {
  const { elements } = dashboard({ missing: ["disable-stitch"] });
  await flush();
  assert.equal(elements.get("profile-name").textContent, "Fixture Creator");
  assert.equal(elements.get("mode-direct").disabled, true);
  assert.match(elements.get("creator-message").textContent, /Dashboard UI version mismatch/);
});
