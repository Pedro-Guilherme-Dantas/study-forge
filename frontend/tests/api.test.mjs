import assert from "node:assert/strict";
import test from "node:test";

async function clientFor(t, respond, sessionResponder) {
  const previousFetch = globalThis.fetch;
  const previousWindow = globalThis.window;
  globalThis.window = new EventTarget();
  const calls = [];
  globalThis.fetch = async (path, options) => {
    calls.push({ path, options });
    if (path === "/api/sessions")
      return sessionResponder
        ? sessionResponder()
        : Response.json({
            session_id: "synthetic",
            csrf_token: "test-only",
            server_instance_id: "instance-a",
          });
    return respond(path, options);
  };
  t.after(() => {
    globalThis.fetch = previousFetch;
    globalThis.window = previousWindow;
  });
  const client = await import(
    `../src/api.ts?case=${encodeURIComponent(t.name)}`
  );
  return { ...client, calls };
}

test("close marks sources discarded only after successful confirmation", async (t) => {
  let accepted = false;
  const client = await clientFor(t, () =>
    accepted
      ? new Response(null, { status: 204 })
      : Response.json(
          { error: { code: "INTERNAL_ERROR", message: "Synthetic failure" } },
          { status: 500 },
        ),
  );
  await assert.rejects(client.api.close("conversation"));
  assert.equal(client.wereTemporarySourcesDiscarded(), false);
  accepted = true;
  await client.api.close("conversation");
  assert.equal(client.wereTemporarySourcesDiscarded(), true);
  assert.equal(
    client.calls.at(-1).options.headers.get("X-CSRF-Token"),
    "test-only",
  );
});

test("instance change signals discard and does not replay a conversation", async (t) => {
  let instance = "instance-a";
  const client = await clientFor(t, () =>
    Response.json({ server_instance_id: instance }),
  );
  let resets = 0;
  window.addEventListener("studyforge:reset", () => resets++);
  await client.getRuntime();
  instance = "instance-b";
  await client.getRuntime();
  assert.equal(resets, 1);
  assert.equal(client.wereTemporarySourcesDiscarded(), true);
  assert.deepEqual(
    client.calls.map(({ path }) => path),
    ["/api/runtime", "/api/runtime"],
  );
});

test("expired session clears context without automatically repeating a mutation", async (t) => {
  const client = await clientFor(t, () =>
    Response.json(
      { error: { code: "SESSION_EXPIRED", message: "Expired" } },
      { status: 410 },
    ),
  );
  await assert.rejects(client.api.turn("old", "Authored question"), {
    code: "SESSION_EXPIRED",
  });
  assert.equal(client.wereTemporarySourcesDiscarded(), true);
  assert.equal(
    client.calls.filter(({ path }) => path.endsWith("/turns")).length,
    1,
  );
});

test("a late session response cannot revive a discarded session or send its mutation", async (t) => {
  let finishOldSession;
  let sessions = 0;
  const client = await clientFor(
    t,
    () => Response.json({ ok: true }),
    () => {
      sessions++;
      if (sessions === 1)
        return new Promise((resolve) => {
          finishOldSession = resolve;
        });
      return Response.json({
        session_id: "new",
        csrf_token: "new-csrf",
        server_instance_id: "instance-b",
      });
    },
  );
  const oldTurn = client.api.turn("old-conversation", "Old authored question");
  client.reset();
  await client.api.progress();
  finishOldSession(
    Response.json({
      session_id: "old",
      csrf_token: "old-csrf",
      server_instance_id: "instance-a",
    }),
  );
  await assert.rejects(oldTurn, { code: "SESSION_EXPIRED" });
  assert.equal(
    client.calls.filter(({ path }) => path.endsWith("/turns")).length,
    0,
  );
  await client.api.turn("new-conversation", "New authored question");
  assert.equal(
    client.calls.at(-1).options.headers.get("X-CSRF-Token"),
    "new-csrf",
  );
  assert.equal(sessions, 2);
});

test("a source response arriving after reset is not returned to the interface", async (t) => {
  let finish;
  let issued;
  const started = new Promise((resolve) => {
    issued = resolve;
  });
  const client = await clientFor(t, () => {
    issued();
    return new Promise((resolve) => {
      finish = resolve;
    });
  });
  const oldSource = client.api.source("old-conversation", "old-source");
  await started;
  client.reset();
  finish(Response.json({ snapshot_text: "DISCARDED_TEST_SOURCE" }));
  await assert.rejects(oldSource, { code: "SESSION_EXPIRED" });
});

test("closing discards a pending source response while preserving the valid session", async (t) => {
  let finish;
  let issued;
  const started = new Promise((resolve) => {
    issued = resolve;
  });
  const client = await clientFor(t, (path, options) => {
    if (path.endsWith("/old-source")) {
      issued();
      return new Promise((resolve) => {
        finish = resolve;
      });
    }
    return options.method === "DELETE"
      ? new Response(null, { status: 204 })
      : Response.json({ ok: true });
  });
  const oldSource = client.api.source("old-conversation", "old-source");
  await started;
  await client.api.close("old-conversation");
  finish(Response.json({ snapshot_text: "DISCARDED_TEST_SOURCE" }));
  await assert.rejects(oldSource, { code: "SESSION_EXPIRED" });
  await client.api.progress();
  assert.equal(
    client.calls.filter(({ path }) => path === "/api/sessions").length,
    1,
  );
});
