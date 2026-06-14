import { useState } from "react";
import { login, register } from "../api/ledgerApi";

export default function LoginForm({ onAuthed }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!username.trim() || !password.trim()) {
      setError("请填写用户名和密码");
      return;
    }

    try {
      const data = isRegister
        ? await register(username.trim(), password.trim())
        : await login(username.trim(), password.trim());

      if (data.ok) {
        onAuthed(data);
      } else {
        setError(data.error || "操作失败");
      }
    } catch (requestError) {
      setError("无法连接后端");
    }
  }

  return (
    <section className="auth-panel">
      <h2>{isRegister ? "注册" : "登录"}</h2>
      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <input
          autoFocus
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          placeholder="用户名"
        />
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="密码"
        />
        <button type="submit">{isRegister ? "注 册" : "登 录"}</button>
      </form>

      <div className="switch">
        {isRegister ? "已有账号？" : "没有账号？"}
        <button type="button" onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? "去登录" : "去注册"}
        </button>
      </div>
    </section>
  );
}
