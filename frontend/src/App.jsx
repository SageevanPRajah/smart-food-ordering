import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import AuthPage from "./pages/AuthPage";
import CartPage from "./pages/CartPage";
import MenuPage from "./pages/MenuPage";
import OrdersPage from "./pages/OrdersPage";
import ReviewsPage from "./pages/ReviewsPage";
import { useState } from "react";

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    const storedUser = localStorage.getItem("current-user");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  const handleLogout = () => {
    localStorage.removeItem("current-user");
    setCurrentUser(null);
  };

  return (
    <Routes>
      <Route element={<Layout currentUser={currentUser} onLogout={handleLogout} />}>
        <Route index element={<Navigate to="/menu" replace />} />
        <Route path="/auth" element={<AuthPage onAuthSuccess={setCurrentUser} />} />
        <Route path="/menu" element={<MenuPage />} />
        <Route path="/cart" element={<CartPage currentUser={currentUser} />} />
        <Route path="/orders" element={<OrdersPage currentUser={currentUser} />} />
        <Route path="/reviews" element={<ReviewsPage currentUser={currentUser} />} />
        <Route path="*" element={<Navigate to="/menu" replace />} />
      </Route>
    </Routes>
  );
}
