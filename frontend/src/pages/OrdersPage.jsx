import { useEffect, useState } from "react";
import api from "../api/client";

const statusOptions = ["Pending", "Processing", "Completed", "Cancelled"];

export default function OrdersPage({ currentUser }) {
  const [orders, setOrders] = useState([]);
  const [searchUserId, setSearchUserId] = useState(currentUser?.user_id || "");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadOrders = async (userId) => {
    try {
      setError("");
      const target = userId ? `/orders/user/${userId}` : "/orders";
      const { data } = await api.get(target);
      setOrders(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load orders.");
    }
  };

  useEffect(() => {
    if (currentUser?.user_id) {
      setSearchUserId(currentUser.user_id);
      loadOrders(currentUser.user_id);
    } else {
      loadOrders("");
    }
  }, [currentUser]);

  const handleSearch = (event) => {
    event.preventDefault();
    loadOrders(searchUserId.trim());
  };

  const updateStatus = async (orderId, status) => {
    try {
      setMessage("");
      setError("");
      await api.patch(`/orders/${orderId}/status`, { status });
      setMessage("Order status updated.");
      loadOrders(searchUserId.trim());
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to update order status.");
    }
  };

  return (
    <section className="single-column-grid">
      <div className="panel">
        <div className="panel-header">
          <div>
            <h1>Orders</h1>
            <p className="muted-text">Track existing orders and update their status for demo purposes.</p>
          </div>
          <form className="search-row" onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="Filter by user ID"
              value={searchUserId}
              onChange={(e) => setSearchUserId(e.target.value)}
            />
            <button className="secondary-button" type="submit">
              Search
            </button>
          </form>
        </div>

        {message && <p className="alert success">{message}</p>}
        {error && <p className="alert error">{error}</p>}

        {orders.length === 0 ? (
          <div className="empty-state">
            <p>No orders found.</p>
          </div>
        ) : (
          <div className="list-stack">
            {orders.map((order) => (
              <div key={order.order_id} className="list-card order-card">
                <div>
                  <h3>Order #{order.order_id}</h3>
                  <p className="small-text">User ID: {order.user_id}</p>
                  <p className="small-text">
                    Date: {new Date(order.order_date).toLocaleString()}
                  </p>
                  <p className="small-text">Total: LKR {Number(order.total).toFixed(2)}</p>
                  <p className="small-text">
                    Items: {order.items.map((item) => `${item.name} x${item.quantity}`).join(", ")}
                  </p>
                </div>

                <div className="inline-controls">
                  <span className="status-badge info">{order.status}</span>
                  <select
                    defaultValue={order.status}
                    onChange={(e) => updateStatus(order.order_id, e.target.value)}
                  >
                    {statusOptions.map((status) => (
                      <option key={status} value={status}>
                        {status}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
