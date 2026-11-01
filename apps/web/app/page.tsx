const features = [
  ["Characters with personality", "Discover original characters with distinct voices, stories and worlds."],
  ["Conversations that remember", "Keep control of your memories and continue conversations with context."],
  ["Create your own universe", "Design characters, shape their stories and share creations when ready."],
];

export default function HomePage() {
  return (
    <main>
      <nav className="nav"><a className="brand" href="/">ALAP<span>✦</span></a><div><a href="#features">Explore</a><a href="#safety">Safety</a><a className="navCta" href="#download">Get the app</a></div></nav>
      <section className="hero">
        <p className="eyebrow">YOUR WORLD. YOUR CHARACTERS.</p>
        <h1>Stories feel different<br/>when <em>they know you.</em></h1>
        <p className="lead">Meet original AI characters, build meaningful fictional worlds and create conversations that are yours to shape.</p>
        <div className="actions"><a className="primary" href="#download">Discover ALAP <span>↗</span></a><a className="secondary" href="#features">Explore the experience</a></div>
        <div className="heroArt" aria-label="Abstract character universe artwork"><div className="orb orbOne"/><div className="orb orbTwo"/><div className="orb orbThree"/><div className="orbit">✦ &nbsp; A universe of characters &nbsp; ✦</div></div>
      </section>
      <section id="features" className="features"><p className="eyebrow">MORE THAN A CHAT</p><h2>A universe built around<br/>the stories you create.</h2><div className="cards">{features.map(([title, body], i) => <article className="feature" key={title}><span>0{i + 1}</span><h3>{title}</h3><p>{body}</p></article>)}</div></section>
      <section id="safety" className="safety"><p className="eyebrow">DESIGNED WITH CONTROL</p><h2>Your experience.<br/>Your boundaries.</h2><p>ALAP is built around transparent AI experiences, user-controlled memory, privacy controls and clear safety boundaries.</p></section>
      <section id="download" className="download"><p className="eyebrow">COMING SOON</p><h2>Find your next story.</h2><p>ALAP is being built. App availability will be announced when the mobile releases are ready.</p></section>
      <footer><a className="brand" href="/">ALAP<span>✦</span></a><p>AI characters are fictional and AI-generated.</p><p>© {new Date().getFullYear()} ALAP</p></footer>
    </main>
  );
}
