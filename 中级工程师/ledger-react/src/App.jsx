import { useEffect, useState } from "react";
import LoginForm from "./components/LoginForm";
import AddRecordForm from "./components/AddRecordForm";
import FilterTabs from "./components/FilterTabs";
import StatsPanel from "./components/StatsPanel";
import RecordTable from "./components/RecordTable";
import {
  createRecord,
  deleteRecord,
  fetchRecords,
  fetchStats
} from "./api/ledgerApi";

const emptyStats = {
  monthly: { "收入": 0, "支出": 0 },
  expense_by_tag: []
};

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("token") || "");
  const [username, setUsername] = useState(() => localStorage.getItem("username") || "");
  const [records, setRecords] = useState([]);
  const [stats, setStats] = useState(emptyStats);
  const [filterType, setFilterType] = useState("");
  const [message, setMessage] = useState("");

  const isAuthed = Boolean(token);

  useEffect(() => {
    if (isAuthed) {
      refresh();
    }
  }, [isAuthed, filterType]);

  function handleAuthed(data) {
    localStorage.setItem("token", data.token);
    localStorage.setItem("username", data.username);
    setToken(data.token);
    setUsername(data.username);
  }

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setToken("");
    setUsername("");
    setRecords([]);
    setStats(emptyStats);
  }

  async function refresh() {
    try {
      const [nextRecords, nextStats] = await Promise.all([
        fetchRecords(token, filterType),
        fetchStats(token)
      ]);
      setRecords(nextRecords);
      setStats(nextStats);
    } catch (error) {
      showMessage("无法加载数据，请确认后端已启动");
    }
  }

  async function handleAddRecord(record) {
    try {
      await createRecord(token, record);
      await refresh();
      showMessage("已记一笔");
    } catch (error) {
      showMessage("添加失败");
    }
  }

  async function handleDeleteRecord(id) {
    try {
      await deleteRecord(token, id);
      await refresh();
    } catch (error) {
      showMessage("删除失败");
    }
  }

  function showMessage(text) {
    setMessage(text);
    window.setTimeout(() => setMessage(""), 2400);
  }

  if (!isAuthed) {
    return <LoginForm onAuthed={handleAuthed} />;
  }

  return (
    <main className="wrap">
      <header className="topbar">
        <div>
          <h1>记账本</h1>
          <span className="user-info">欢迎，{username}</span>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          退出
        </button>
      </header>

      <AddRecordForm onSubmit={handleAddRecord} />
      <FilterTabs value={filterType} onChange={setFilterType} />
      <StatsPanel stats={stats} />
      <RecordTable records={records} onDelete={handleDeleteRecord} />

      {message && <div className="toast">{message}</div>}
    </main>
  );
}
