import { Link, NavLink } from "react-router-dom";
import { useCart } from "../context/CartContext";

export default function NavBar({ currentUser, onLogout }) {
  const { totalItems } = useCart();

  return (
    <header className="topbar">
      <div className="brand-wrapper">
        <Link className="brand" to="/menu">
          Smart Food Ordering
        </Link>
        <span className="subtitle">FastAPI + MongoDB + React Microservices Demo</span>
      </div>

      <nav className="nav-links">
        <NavLink to="/auth">Login/Register</NavLink>
        <NavLink to="/menu">Menu</NavLink>
        <NavLink to="/cart">Cart ({totalItems})</NavLink>
        <NavLink to="/orders">Orders</NavLink>
        <NavLink to="/reviews">Reviews</NavLink>
      </nav>

      <div className="user-area">
        {currentUser ? (
          <>
            <span className="user-badge">Logged in: {currentUser.name}</span>
            <button className="secondary-button" onClick={onLogout}>
              Logout
            </button>
          </>
        ) : (
          <span className="user-badge muted">Guest</span>
        )}
      </div>
    </header>
  );
}
