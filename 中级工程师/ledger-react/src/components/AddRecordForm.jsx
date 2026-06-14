import { useState } from "react";

const incomeTags = ["工资", "兼职", "理财", "其他"];
const expenseTags = ["餐饮", "交通", "购物", "住房", "娱乐", "其他"];

function today() {
  return new Date().toISOString().slice(0, 10);
}

export default function AddRecordForm({ onSubmit }) {
  const [date, setDate] = useState(today());
  const [type, setType] = useState("支出");
  const [tag, setTag] = useState("餐饮");
  const [item, setItem] = useState("");
  const [amount, setAmount] = useState("");

  const tags = type === "收入" ? incomeTags : expenseTags;

  function handleTypeChange(nextType) {
    setType(nextType);
    setTag(nextType === "收入" ? incomeTags[0] : expenseTags[0]);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const value = Number(amount);

    if (!value || value <= 0) {
      return;
    }

    await onSubmit({
      date,
      type,
      tag,
      item,
      amount: value
    });

    setItem("");
    setAmount("");
  }

  return (
    <form className="form-row" onSubmit={handleSubmit}>
      <input type="date" value={date} onChange={(event) => setDate(event.target.value)} />
      <select value={type} onChange={(event) => handleTypeChange(event.target.value)}>
        <option value="支出">支出</option>
        <option value="收入">收入</option>
      </select>
      <select value={tag} onChange={(event) => setTag(event.target.value)}>
        {tags.map((name) => (
          <option key={name} value={name}>
            {name}
          </option>
        ))}
      </select>
      <input
        className="item-input"
        value={item}
        onChange={(event) => setItem(event.target.value)}
        placeholder="备注（选填）"
      />
      <input
        className="amount-input"
        type="number"
        value={amount}
        onChange={(event) => setAmount(event.target.value)}
        placeholder="金额"
        step="0.01"
        min="0"
      />
      <button type="submit">记一笔</button>
    </form>
  );
}
