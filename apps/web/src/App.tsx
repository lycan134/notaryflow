import './App.css'

const stats = [
  {
    label: 'Total Clients',
    value: '24',
    description: 'Registered clients',
  },
  {
    label: 'Active Transactions',
    value: '12',
    description: 'Currently in progress',
  },
  {
    label: 'For Review',
    value: '5',
    description: 'Documents need attention',
  },
  {
    label: 'Completed',
    value: '18',
    description: 'Transactions completed',
  },
]

const recentTransactions = [
  {
    reference: 'NF-2026-0012',
    client: 'Maria Santos',
    type: 'Special Power of Attorney',
    status: 'UNDER_REVIEW',
    date: 'Sep 12, 2026',
  },
  {
    reference: 'NF-2026-0011',
    client: 'Juan Dela Cruz',
    type: 'Deed of Sale',
    status: 'REVIEWED',
    date: 'Sep 11, 2026',
  },
  {
    reference: 'NF-2026-0010',
    client: 'Ana Reyes',
    type: 'Affidavit',
    status: 'UPLOADED',
    date: 'Sep 10, 2026',
  },
  {
    reference: 'NF-2026-0009',
    client: 'Carlos Mendoza',
    type: 'Acknowledgment',
    status: 'REJECTED',
    date: 'Sep 9, 2026',
  },
]

function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">N</div>
          <div>
            <div className="brand-name">NotaryFlow</div>
            <div className="brand-subtitle">Office Workflow</div>
          </div>
        </div>

        <nav className="navigation" aria-label="Main navigation">
          <a className="nav-item active" href="#dashboard">
            <span>âŒ‚</span>
            Dashboard
          </a>

          <a className="nav-item" href="#clients">
            <span>â™™</span>
            Clients
          </a>

          <a className="nav-item" href="#transactions">
            <span>â–£</span>
            Transactions
          </a>

          <a className="nav-item" href="#documents">
            <span>â–¡</span>
            Documents
          </a>

          <a className="nav-item" href="#reports">
            <span>â–¤</span>
            Reports
          </a>
        </nav>

        <div className="sidebar-footer">
          <div className="office-label">Current office</div>
          <div className="office-name">NotaryFlow Development Office</div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Workspace</p>
            <h1>Dashboard</h1>
          </div>

          <div className="user-menu">
            <div className="user-avatar">ND</div>
            <div>
              <div className="user-name">NotaryFlow Development</div>
              <div className="user-role">Administrator</div>
            </div>
          </div>
        </header>

        <section className="dashboard-content" id="dashboard">
          <div className="welcome">
            <div>
              <h2>Good morning</h2>
              <p>
                Here is an overview of your office&apos;s administrative
                workflow.
              </p>
            </div>

            <button type="button" className="primary-button">
              + New Transaction
            </button>
          </div>

          <section className="stats-grid" aria-label="Office statistics">
            {stats.map((stat) => (
              <article className="stat-card" key={stat.label}>
                <p className="stat-label">{stat.label}</p>
                <p className="stat-value">{stat.value}</p>
                <p className="stat-description">{stat.description}</p>
              </article>
            ))}
          </section>

          <section className="dashboard-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Activity</p>
                <h2>Recent transactions</h2>
              </div>

              <button type="button" className="secondary-button">
                View all
              </button>
            </div>

            <div className="transaction-table-wrapper">
              <table className="transaction-table">
                <thead>
                  <tr>
                    <th>Reference</th>
                    <th>Client</th>
                    <th>Transaction</th>
                    <th>Status</th>
                    <th>Date received</th>
                  </tr>
                </thead>

                <tbody>
                  {recentTransactions.map((transaction) => (
                    <tr key={transaction.reference}>
                      <td className="reference">
                        {transaction.reference}
                      </td>
                      <td>{transaction.client}</td>
                      <td>{transaction.type}</td>
                      <td>
                        <span
                          className={`status-badge status-${transaction.status.toLowerCase()}`}
                        >
                          {transaction.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td>{transaction.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="review-notice">
            <div className="notice-icon">!</div>
            <div>
              <strong>Administrative review</strong>
              <p>
                Document review in NotaryFlow tracks workflow and completeness.
                It does not determine legal validity or replace the
                notary&apos;s professional judgment.
              </p>
            </div>
          </section>
        </section>
      </main>
    </div>
  )
}

export default App
