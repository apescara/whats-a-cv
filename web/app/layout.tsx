import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "What's a CV?",
  description: "A local-first workspace for targeted job applications.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const navigation = [
    ["Profile", "/"],
    ["Create CV", "/create-cv"],
    ["Applications", "/applications"],
    ["Assistant", "/assistant"],
    ["Lab", "/lab"],
    ["Settings", "/settings"],
  ];

  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main-content">
          Skip to main content
        </a>
        <div className="app-shell">
          <aside className="sidebar" aria-label="Primary navigation">
            <a className="brand" href="/" aria-label="What&apos;s a CV? home">
              What&apos;s a CV?
            </a>
            <nav>
              <ul className="nav-list">
                {navigation.map(([label, href]) => (
                  <li key={href}>
                    <a className="nav-link" href={href}>
                      {label}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          </aside>
          <div className="app-content">
            <header className="app-header">
              <p className="eyebrow">Candidate workspace</p>
              <span className="header-status">Local-first</span>
            </header>
            <main id="main-content">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
