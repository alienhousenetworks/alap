"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

type Character = { id: string; name: string; description: string; greeting: string; moderation_status: string; visibility: string; owner_id: string | null };
type AuditItem = { id: string; actor_user_id: string | null; character_id: string | null; action: string; reason: string | null; created_at: string };

export default function AdminConsole() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [signedIn, setSignedIn] = useState(false);
  const [items, setItems] = useState<Character[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"queue" | "audit">("queue");
  const [audit, setAudit] = useState<AuditItem[]>([]);

  const load = useCallback(async () => {
    const response = await fetch("/api/admin/moderation", { cache: "no-store" });
    if (response.status === 401) { setSignedIn(false); return; }
    if (response.status === 403) throw new Error("This account does not have administrator access.");
    if (!response.ok) throw new Error("Could not load moderation queue.");
    setItems(await response.json());
    setSignedIn(true);
  }, []);

  useEffect(() => { load().catch((e: Error) => setError(e.message)); }, [load]);

  async function loadAudit() {
    const response = await fetch("/api/admin/audit", { cache: "no-store" });
    if (!response.ok) throw new Error("Could not load moderation audit history.");
    setAudit(await response.json());
  }

  async function login(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      const response = await fetch("/api/admin/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
      if (!response.ok) throw new Error("Sign-in failed. Check credentials and administrator role.");
      setPassword(""); await load();
    } catch (e) { setError(e instanceof Error ? e.message : "Sign-in failed."); }
    finally { setBusy(false); }
  }

  async function decide(id: string, decision: "approve" | "reject") {
    setBusy(true); setError("");
    try {
      const response = await fetch("/api/admin/moderation/" + encodeURIComponent(id) + "/" + decision, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: decision === "reject" ? "Does not meet ALAP character publishing standards." : "" }),
      });
      if (!response.ok) throw new Error("Moderation action failed.");
      await load();
    } catch (e) { setError(e instanceof Error ? e.message : "Moderation action failed."); }
    finally { setBusy(false); }
  }

  async function logout() {
    await fetch("/api/admin/logout", { method: "POST" });
    setSignedIn(false); setItems([]);
  }

  return <main style={{maxWidth:1100,margin:"0 auto",padding:"48px 24px"}}>
    <header style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:16}}>
      <div><p style={{color:"#c5f36a",letterSpacing:3,fontSize:11,fontWeight:700}}>ALAP / OPERATIONS</p><h1 style={{fontSize:40,letterSpacing:-1}}>Control room</h1></div>
      {signedIn && <button onClick={logout}>Sign out</button>}
    </header>
    {error && <p role="alert" style={{color:"#ff8d8d",padding:12,background:"#391e25",borderRadius:8}}>{error}</p>}
    {!signedIn ? <form onSubmit={login} style={{maxWidth:420,display:"grid",gap:14,marginTop:32}}>
      <h2>Administrator sign in</h2>
      <label>Email<input required type="email" autoComplete="username" value={email} onChange={e=>setEmail(e.target.value)} style={field}/></label>
      <label>Password<input required type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} style={field}/></label>
      <button disabled={busy} type="submit">{busy ? "Signing in…" : "Sign in"}</button>
      <p style={{color:"#9299a5",fontSize:12}}>Access is enforced by the API administrator role. This console does not grant privileges to ordinary accounts.</p>
    </form> : <section style={{marginTop:30}}>
      <div style={{display:"flex",gap:10,marginBottom:24}}>
        <button onClick={()=>setTab("queue")}>Pending queue ({items.length})</button>
        <button onClick={()=>{setTab("audit");loadAudit().catch((e:Error)=>setError(e.message));}}>Audit history</button>
      </div>
      {tab === "queue" ? <>
        <h2>Character moderation queue</h2>
        {items.length === 0 ? <p style={{color:"#9299a5",padding:24,background:"#151a22",borderRadius:12}}>No characters awaiting review.</p> : items.map(item=><article key={item.id} style={{padding:22,marginBottom:14,border:"1px solid #ffffff20",borderRadius:14,background:"#151a22"}}>
          <div style={{display:"flex",justifyContent:"space-between",gap:16,flexWrap:"wrap"}}><div><small style={{color:"#c5f36a"}}>{item.visibility.toUpperCase()} · {item.moderation_status.toUpperCase()}</small><h3>{item.name}</h3></div><code>{item.id.slice(0,8)}</code></div>
          <p style={{color:"#c2c6ce"}}>{item.description}</p><blockquote style={{margin:0,padding:12,borderLeft:"2px solid #c5f36a",color:"#9299a5"}}>{item.greeting || "No opening greeting"}</blockquote>
          <div style={{display:"flex",gap:10,marginTop:18}}><button disabled={busy} onClick={()=>decide(item.id,"approve")}>Approve</button><button disabled={busy} onClick={()=>decide(item.id,"reject")}>Reject</button></div>
        </article>)}
      </> : <>
        <h2>Moderation audit history</h2>
        {audit.length === 0 ? <p style={{color:"#9299a5"}}>No moderation actions recorded.</p> : audit.map(entry=><article key={entry.id} style={{padding:18,marginBottom:10,border:"1px solid #ffffff20",borderRadius:12,background:"#151a22"}}>
          <div style={{display:"flex",justifyContent:"space-between",gap:12}}><strong>{entry.action.toUpperCase()}</strong><small style={{color:"#9299a5"}}>{new Date(entry.created_at).toLocaleString()}</small></div>
          <p style={{color:"#c2c6ce"}}>{entry.reason || "No reason supplied"}</p>
          <small style={{color:"#9299a5"}}>Character: {entry.character_id || "Deleted"} · Moderator: {entry.actor_user_id || "Deleted"}</small>
        </article>)}
      </>}
    </section>}
  </main>;
}

const field = { display:"block",width:"100%",padding:12,marginTop:6,boxSizing:"border-box" as const,borderRadius:8,border:"1px solid #3b424d",background:"#171c25",color:"#fff" };
