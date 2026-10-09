import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const API_BASE = "https://fin-health-system.onrender.com"; 

export default function Signup() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("https://fin-health-system.onrender.com/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }), // make sure these match your state variables
      });

      if (!response.ok) {
        const errData = await response.json();
        alert("Error: " + (errData.detail || "Signup failed"));
        return;
      }

      alert("Account created successfully! You can now log in.");
      window.location.href = "/login"; // Instantly routes to your login page
      
    } catch (err) {
      alert("Network error: " + err.message);
    }
  };