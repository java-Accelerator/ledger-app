export default function StatsPanel({ stats }) {
  const monthly = stats.monthly || { "收入": 0, "支出": 0 };
  const income = Number(monthly["收入"] || 0);
  const expense = Number(monthly["支出"] || 0);
  const balance = income - expense;
  const balanceStatus = getBalanceStatus(balance);

  return (
    <>
      <section className="stats">
        <div className="stat-item">
          <div className="label">本月收入</div>
          <div className="value income">{income.toFixed(2)}</div>
        </div>
        <div className="stat-item">
          <div className="label">本月支出</div>
          <div className="value expense">{expense.toFixed(2)}</div>
        </div>
        <div className="stat-item">
          <div className="label">本月结余</div>
          <div className="value">{balance.toFixed(2)}</div>
        </div>
        <div className="stat-item status-item">
          <div className="label">状态</div>
          <div className={`status-text ${balanceStatus.kind}`}>{balanceStatus.text}</div>
        </div>
      </section>
      <TagBars title="收入分类" kind="income" tags={stats.income_by_tag || []} />
      <TagBars title="支出分类" kind="expense" tags={stats.expense_by_tag || []} />
    </>
  );
}

function getBalanceStatus(balance) {
  if (balance > 0) {
    return { text: "本月有结余", kind: "good" };
  }

  if (balance < 0) {
    return { text: "本月超支", kind: "bad" };
  }

  return { text: "刚好持平", kind: "neutral" };
}

function TagBars({ title, kind, tags }) {
  if (!tags.length) {
    return null;
  }

  const max = Math.max(...tags.map((tag) => Number(tag.amount) || 0), 1);

  return (
    <section className="tag-bars">
      <h2 className="tag-section-title">{title}</h2>
      {tags.map((tag) => (
        <div className="tag-bar-row" key={tag.tag}>
          <span className="tag-name">{tag.tag}</span>
          <div className="bar-wrap">
            <div className={`bar ${kind}`} style={{ width: `${(tag.amount / max) * 100}%` }} />
          </div>
          <span className="tag-amount">{Number(tag.amount).toFixed(2)}</span>
        </div>
      ))}
    </section>
  );
}
