import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

const initialRegisterState = {
  name: "",
  phone: "",
  email: "",
  password: ""
};

const initialLoginState = {
  email: "",
  password: ""
};

export default function AuthPage({ onAuthSuccess }) {
  const [activeTab, setActiveTab] = useState("login");
  const [registerForm, setRegisterForm] = useState(initialRegisterState);
  const [loginForm, setLoginForm] = useState(initialLoginState);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      const { data } = await api.post("/users/register", registerForm);
      localStorage.setItem("current-user", JSON.stringify(data));
      onAuthSuccess(data);
      setMessage("Registration successful.");
      setRegisterForm(initialRegisterState);
      navigate("/menu");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to register user.");
    }
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");
    try {
      const { data } = await api.post("/users/login", loginForm);
      localStorage.setItem("current-user", JSON.stringify(data.user));
      onAuthSuccess(data.user);
      setMessage(data.message);
      setLoginForm(initialLoginState);
      navigate("/menu");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to login user.");
    }
  };

  return (
    <section className="two-column-grid">
      <div className="panel">
        <h1>Login / Register</h1>
        <p className="muted-text">
          Create an account or log in to place food orders, make payments, and add reviews.
        </p>

        <div className="tab-row">
          <button
            className={activeTab === "login" ? "tab active-tab" : "tab"}
            onClick={() => setActiveTab("login")}
          >
            Login
          </button>
          <button
            className={activeTab === "register" ? "tab active-tab" : "tab"}
            onClick={() => setActiveTab("register")}
          >
            Register
          </button>
        </div>

        {activeTab === "login" ? (
          <form className="form-grid" onSubmit={handleLogin}>
            <label>
              Email
              <input
                type="email"
                value={loginForm.email}
                onChange={(e) =>
                  setLoginForm((current) => ({ ...current, email: e.target.value }))
                }
                required
              />
            </label>
            <label>
              Password
              <input
                type="password"
                value={loginForm.password}
                onChange={(e) =>
                  setLoginForm((current) => ({ ...current, password: e.target.value }))
                }
                required
              />
            </label>
            <button className="primary-button" type="submit">
              Login
            </button>
          </form>
        ) : (
          <form className="form-grid" onSubmit={handleRegister}>
            <label>
              Name
              <input
                type="text"
                value={registerForm.name}
                onChange={(e) =>
                  setRegisterForm((current) => ({ ...current, name: e.target.value }))
                }
                required
              />
            </label>
            <label>
              Phone
              <input
                type="text"
                value={registerForm.phone}
                onChange={(e) =>
                  setRegisterForm((current) => ({ ...current, phone: e.target.value }))
                }
                required
              />
            </label>
            <label>
              Email
              <input
                type="email"
                value={registerForm.email}
                onChange={(e) =>
                  setRegisterForm((current) => ({ ...current, email: e.target.value }))
                }
                required
              />
            </label>
            <label>
              Password
              <input
                type="password"
                value={registerForm.password}
                onChange={(e) =>
                  setRegisterForm((current) => ({ ...current, password: e.target.value }))
                }
                required
              />
            </label>
            <button className="primary-button" type="submit">
              Register
            </button>
          </form>
        )}

        {message && <p className="alert success">{message}</p>}
        {error && <p className="alert error">{error}</p>}
      </div>

      <div className="panel highlight-panel">
        <h2>Demo Flow</h2>
        <ol className="ordered-list">
          <li>Register or login.</li>
          <li>Open the menu and add food items to cart.</li>
          <li>Create an order from the cart page.</li>
          <li>Generate a payment record using Cash on Delivery.</li>
          <li>Track orders and add reviews from the review page.</li>
        </ol>
      </div>
    </section>
  );
}
