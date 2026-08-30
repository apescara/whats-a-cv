export default function Home() {
  return (
    <section className="home">
      <div className="welcome-panel">
        <p className="welcome-mark">What&apos;s a CV?</p>
        <h1>Your career story, ready when opportunity calls.</h1>
        <p className="lede">Keep your complete work history in one place. When you find a role, use that evidence to prepare a truthful, tailored application.</p>
        <div className="action-row">
          <a className="button button-primary" href="/profile">Build your profile</a>
          <a className="button button-secondary" href="/applications">Review applications</a>
        </div>
      </div>
      <section className="getting-started" aria-labelledby="getting-started-title">
        <h2 id="getting-started-title">A simple place to start</h2>
        <ol>
          <li><strong>Add your experience.</strong> Capture roles, achievements, education, and skills once.</li>
          <li><strong>Keep it current.</strong> Your profile remains the source for every application.</li>
          <li><strong>Tailor with confidence.</strong> Review suggested changes before anything is saved.</li>
        </ol>
      </section>
      <p className="privacy-note"><strong>Everything stays yours.</strong> Your career records live in this workspace and proposed AI changes are always reviewable.</p>
    </section>
  );
}
