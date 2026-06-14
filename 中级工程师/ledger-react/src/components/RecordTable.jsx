export default function RecordTable({ records, onDelete }) {
  const totalAmount = records.reduce((sum, record) => sum + Number(record.amount || 0), 0);

  return (
    <table className="records-table">
      <thead>
        <tr>
          <th>日期</th>
          <th>类型</th>
          <th>分类</th>
          <th>备注</th>
          <th className="amount-col">金额</th>
          <th className="action-col"></th>
        </tr>
      </thead>
      <tbody>
        {records.length === 0 ? (
          <tr>
            <td className="empty-hint" colSpan="6">
              暂无记录，记一笔吧
            </td>
          </tr>
        ) : (
          records.map((record) => <RecordRow key={record.id} record={record} onDelete={onDelete} />)
        )}
      </tbody>
      <tfoot>
        <tr>
          <td colSpan="4">当前列表合计</td>
          <td className="amount-col">{totalAmount.toFixed(2)}</td>
          <td></td>
        </tr>
      </tfoot>
    </table>
  );
}

function RecordRow({ record, onDelete }) {
  const kind = record.type === "收入" ? "income" : "expense";

  return (
    <tr>
      <td>{record.date}</td>
      <td>
        <span className={`type-tag ${kind}`}>{record.type}</span>
      </td>
      <td>{record.tag}</td>
      <td>{record.item || "-"}</td>
      <td className={`amount-col ${kind}`}>{Number(record.amount).toFixed(2)}</td>
      <td>
        <button className="del-btn" onClick={() => onDelete(record.id)} type="button">
          x
        </button>
      </td>
    </tr>
  );
}
