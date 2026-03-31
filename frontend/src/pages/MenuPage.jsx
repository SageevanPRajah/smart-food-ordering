import { useEffect, useState } from "react";
import api from "../api/client";
import MenuCard from "../components/MenuCard";
import { useCart } from "../context/CartContext";

const sampleProducts = [
  { name: "Chicken Burger", category: "Burger", price: 1250, availability: true },
  { name: "Veggie Pizza", category: "Pizza", price: 2100, availability: true },
  { name: "Iced Coffee", category: "Beverage", price: 650, availability: true }
];

export default function MenuPage() {
  const [products, setProducts] = useState([]);
  const [formState, setFormState] = useState({
    name: "",
    category: "",
    price: "",
    availability: true
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const { addItem } = useCart();

  const loadProducts = async () => {
    try {
      const { data } = await api.get("/products");
      setProducts(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load menu items.");
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleAddProduct = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      await api.post("/products", {
        ...formState,
        price: Number(formState.price)
      });
      setFormState({ name: "", category: "", price: "", availability: true });
      setMessage("Menu item added successfully.");
      loadProducts();
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to add product.");
    }
  };

  const seedSampleProducts = async () => {
    try {
      setError("");
      setMessage("");
      await Promise.all(sampleProducts.map((item) => api.post("/products", item)));
      setMessage("Sample menu items inserted.");
      loadProducts();
    } catch {
      setError("Unable to seed sample products. They may already exist or the service may be down.");
    }
  };

  return (
    <section className="two-column-grid">
      <div className="panel wide-panel">
        <div className="panel-header">
          <div>
            <h1>Menu Listing</h1>
            <p className="muted-text">Browse available menu items and add them to the cart.</p>
          </div>
          <button className="secondary-button" onClick={seedSampleProducts}>
            Insert sample menu
          </button>
        </div>

        {products.length === 0 ? (
          <div className="empty-state">
            <p>No menu items found yet.</p>
            <p className="muted-text">Use the form on the right or click "Insert sample menu".</p>
          </div>
        ) : (
          <div className="card-grid">
            {products.map((product) => (
              <MenuCard key={product.item_id} product={product} onAddToCart={addItem} />
            ))}
          </div>
        )}
      </div>

      <div className="panel">
        <h2>Add Menu Item</h2>
        <form className="form-grid" onSubmit={handleAddProduct}>
          <label>
            Name
            <input
              type="text"
              value={formState.name}
              onChange={(e) => setFormState((current) => ({ ...current, name: e.target.value }))}
              required
            />
          </label>
          <label>
            Category
            <input
              type="text"
              value={formState.category}
              onChange={(e) => setFormState((current) => ({ ...current, category: e.target.value }))}
              required
            />
          </label>
          <label>
            Price
            <input
              type="number"
              min="1"
              step="0.01"
              value={formState.price}
              onChange={(e) => setFormState((current) => ({ ...current, price: e.target.value }))}
              required
            />
          </label>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={formState.availability}
              onChange={(e) =>
                setFormState((current) => ({ ...current, availability: e.target.checked }))
              }
            />
            Available
          </label>
          <button className="primary-button" type="submit">
            Save Menu Item
          </button>
        </form>

        {message && <p className="alert success">{message}</p>}
        {error && <p className="alert error">{error}</p>}
      </div>
    </section>
  );
}
