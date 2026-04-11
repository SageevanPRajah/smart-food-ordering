import { Outlet } from "react-router-dom";
import NavBar from "./NavBar";

export default function Layout({ currentUser, onLogout }) {
  return (
    <div className="app-shell">
      <NavBar currentUser={currentUser} onLogout={onLogout} />
      <main className="page-shell">
        <Outlet />
      </main>
    </div>
  );
}
