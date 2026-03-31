export default function MenuCard({ product, onAddToCart }) {
  return (
    <div className="card">
      <div className="card-head">
        <h3>{product.name}</h3>
        <span className={product.availability ? "status-badge success" : "status-badge danger"}>
          {product.availability ? "Available" : "Unavailable"}
        </span>
      </div>
      <p className="small-text">Category: {product.category}</p>
      <p className="price-text">LKR {Number(product.price).toFixed(2)}</p>
      <button
        className="primary-button"
        disabled={!product.availability}
        onClick={() => onAddToCart(product)}
      >
        Add to cart
      </button>
    </div>
  );
}
