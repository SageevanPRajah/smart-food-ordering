import { useState } from "react";
import api from "../api/client";
import { useCart } from "../context/CartContext";

export default function CartPage({ currentUser }) {
  const { cartItems, updateQuantity, removeItem, totalAmount, clearCart } = useCart();
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastOrder, setLastOrder] = useState(null);
  const [lastPayment, setLastPayment] = useState(null);

  const handleCheckout = async () => {
    if (!currentUser) {
      setError("Please login before placing an order.");
      return;
    }

    if (cartItems.length === 0) {
      setError("Your cart is empty.");
      return;
    }

    setError("");
    setMessage("");
    setLoading(true);

    try {
      const orderPayload = {
        user_id: currentUser.user_id,
        items: cartItems.map((item) => ({
          item_id: item.item_id,
          name: item.name,
          price: Number(item.price),
          quantity: Number(item.quantity)
        }))
      };

      const orderResponse = await api.post("/orders", orderPayload);
      const paymentResponse = await api.post("/payments", {
        order_id: orderResponse.data.order_id,
        method: "Cash on Delivery",
        amount: Number(orderResponse.data.total)
      });

      setLastOrder(orderResponse.data);
      setLastPayment(paymentResponse.data);
      clearCart();
      setMessage("Order placed and payment record created successfully.");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to place order.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="two-column-grid">
      <div className="panel wide-panel">
        <h1>Cart</h1>
        {cartItems.length === 0 ? (
          <div className="empty-state">
            <p>Your cart is empty.</p>
            <p className="muted-text">Add items from the menu page.</p>
          </div>
        ) : (
          <div className="list-stack">
            {cartItems.map((item) => (
              <div key={item.item_id} className="list-card">
                <div>
                  <h3>{item.name}</h3>
                  <p className="small-text">{item.category}</p>
                  <p className="small-text">LKR {Number(item.price).toFixed(2)} each</p>
                </div>
                <div className="inline-controls">
                  <button
                    className="small-button"
                    onClick={() => updateQuantity(item.item_id, item.quantity - 1)}
                  >
                    -
                  </button>
                  <span>{item.quantity}</span>
                  <button
                    className="small-button"
                    onClick={() => updateQuantity(item.item_id, item.quantity + 1)}
                  >
                    +
                  </button>
                  <button className="danger-button" onClick={() => removeItem(item.item_id)}>
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {message && <p className="alert success">{message}</p>}
        {error && <p className="alert error">{error}</p>}
      </div>

      <div className="panel">
        <h2>Order Summary</h2>
        <p className="summary-line">
          <span>Current user</span>
          <strong>{currentUser ? currentUser.name : "Not logged in"}</strong>
        </p>
        <p className="summary-line">
          <span>User ID</span>
          <strong>{currentUser ? currentUser.user_id : "N/A"}</strong>
        </p>
        <p className="summary-line">
          <span>Total</span>
          <strong>LKR {Number(totalAmount).toFixed(2)}</strong>
        </p>

        <button className="primary-button full-width" disabled={loading} onClick={handleCheckout}>
          {loading ? "Processing..." : "Place Order"}
        </button>

        {lastOrder && (
          <div className="summary-box">
            <h3>Last Order</h3>
            <p>Order ID: {lastOrder.order_id}</p>
            <p>Status: {lastOrder.status}</p>
            <p>Total: LKR {Number(lastOrder.total).toFixed(2)}</p>
          </div>
        )}

        {lastPayment && (
          <div className="summary-box">
            <h3>Payment Record</h3>
            <p>Payment ID: {lastPayment.payment_id}</p>
            <p>Method: {lastPayment.method}</p>
            <p>Status: {lastPayment.status}</p>
          </div>
        )}
      </div>
    </section>
  );
}
