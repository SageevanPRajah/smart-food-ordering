import { useEffect, useState } from "react";
import api from "../api/client";

export default function ReviewsPage({ currentUser }) {
  const [products, setProducts] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [summary, setSummary] = useState(null);
  const [formState, setFormState] = useState({
    item_id: "",
    rating: 5,
    comments: ""
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadProducts = async () => {
    const { data } = await api.get("/products");
    setProducts(data);
    if (data.length > 0 && !formState.item_id) {
      setFormState((current) => ({ ...current, item_id: data[0].item_id }));
    }
  };

  const loadReviews = async (itemId = "") => {
    try {
      const endpoint = itemId ? `/reviews/item/${itemId}` : "/reviews";
      const { data } = await api.get(endpoint);
      setReviews(data);

      if (itemId) {
        const summaryResponse = await api.get(`/reviews/item/${itemId}/summary`);
        setSummary(summaryResponse.data);
      } else {
        setSummary(null);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load reviews.");
    }
  };

  useEffect(() => {
    loadProducts()
      .then(() => loadReviews(""))
      .catch(() => setError("Unable to load reviews page data."));
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!currentUser) {
      setError("Please login before adding a review.");
      return;
    }

    try {
      setError("");
      setMessage("");
      await api.post("/reviews", {
        user_id: currentUser.user_id,
        item_id: formState.item_id,
        rating: Number(formState.rating),
        comments: formState.comments
      });
      setMessage("Review submitted successfully.");
      setFormState((current) => ({ ...current, rating: 5, comments: "" }));
      loadReviews(formState.item_id);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to submit review.");
    }
  };

  const handleFilter = async (itemId) => {
    setFormState((current) => ({ ...current, item_id: itemId }));
    loadReviews(itemId);
  };

  return (
    <section className="two-column-grid">
      <div className="panel wide-panel">
        <div className="panel-header">
          <div>
            <h1>Reviews</h1>
            <p className="muted-text">Read ratings and feedback for menu items.</p>
          </div>
          <select value={formState.item_id} onChange={(e) => handleFilter(e.target.value)}>
            <option value="">All Items</option>
            {products.map((product) => (
              <option key={product.item_id} value={product.item_id}>
                {product.name}
              </option>
            ))}
          </select>
        </div>

        {summary && (
          <div className="summary-box">
            <h3>Selected Item Summary</h3>
            <p>Average Rating: {summary.average_rating}</p>
            <p>Total Reviews: {summary.total_reviews}</p>
          </div>
        )}

        {reviews.length === 0 ? (
          <div className="empty-state">
            <p>No reviews found.</p>
          </div>
        ) : (
          <div className="list-stack">
            {reviews.map((review) => (
              <div key={review.review_id} className="list-card">
                <div>
                  <h3>Rating: {review.rating}/5</h3>
                  <p className="small-text">User ID: {review.user_id}</p>
                  <p className="small-text">Item ID: {review.item_id}</p>
                </div>
                <p>{review.comments}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="panel">
        <h2>Add Review</h2>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Product
            <select
              value={formState.item_id}
              onChange={(e) => setFormState((current) => ({ ...current, item_id: e.target.value }))}
              required
            >
              {products.map((product) => (
                <option key={product.item_id} value={product.item_id}>
                  {product.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Rating
            <input
              type="number"
              min="1"
              max="5"
              value={formState.rating}
              onChange={(e) => setFormState((current) => ({ ...current, rating: e.target.value }))}
              required
            />
          </label>
          <label>
            Comments
            <textarea
              rows="4"
              value={formState.comments}
              onChange={(e) => setFormState((current) => ({ ...current, comments: e.target.value }))}
              required
            />
          </label>
          <button className="primary-button" type="submit">
            Submit Review
          </button>
        </form>

        {message && <p className="alert success">{message}</p>}
        {error && <p className="alert error">{error}</p>}
      </div>
    </section>
  );
}
