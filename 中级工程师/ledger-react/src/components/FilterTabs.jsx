const tabs = [
  { label: "全部", value: "" },
  { label: "收入", value: "收入" },
  { label: "支出", value: "支出" }
];

export default function FilterTabs({ value, onChange }) {
  return (
    <div className="tabs">
      {tabs.map((tab) => (
        <button
          key={tab.label}
          className={value === tab.value ? "active" : ""}
          onClick={() => onChange(tab.value)}
          type="button"
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
