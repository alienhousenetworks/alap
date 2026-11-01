const modules = ["User & account operations", "Character catalogue & publishing", "Moderation review queue", "AI provider health & usage", "Subscriptions & billing reconciliation", "Wallet ledger & credit adjustments", "Product analytics & audit trail"];

export default function AdminHome() {
  return <main style={{maxWidth:1100,margin:"0 auto",padding:"64px 28px"}}>
    <p style={{color:"#c5f36a",letterSpacing:3,fontSize:11,fontWeight:700}}>ALAP / OPERATIONS</p>
    <h1 style={{fontSize:48,letterSpacing:-2}}>Control room</h1>
    <p style={{color:"#a9adb5",maxWidth:650,lineHeight:1.7}}>Administrative modules are being implemented. This console must be protected by server-side admin roles and MFA before deployment; hiding routes in the UI is not authorization.</p>
    <section style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(240px,1fr))",gap:14,marginTop:36}}>
      {modules.map((m,i)=><article key={m} style={{border:"1px solid #ffffff20",background:"#151a22",borderRadius:14,padding:22}}><small style={{color:"#c5f36a"}}>MODULE 0{i+1}</small><h3>{m}</h3><p style={{color:"#8f96a1",fontSize:13}}>Not connected to production services yet.</p></article>)}
    </section>
  </main>;
}
