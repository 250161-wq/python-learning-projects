import React, { useState, useEffect } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Container,
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Link,
  Alert,
  CircularProgress,
} from '@mui/material';
import { RootState, AppDispatch } from '../store';
import { register, clearError } from '../store/slices/authSlice';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { loading, error } = useSelector((state: RootState) => state.auth);

  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [validationError, setValidationError] = useState('');

  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError('');

    if (formData.password !== formData.confirmPassword) {
      setValidationError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setValidationError('Password must be at least 8 characters');
      return;
    }

    const result = await dispatch(register({
      email: formData.email,
      username: formData.username,
      password: formData.password,
      full_name: formData.full_name || undefined,
    }));

    if (!result.type.endsWith('rejected')) {
      navigate('/login', { state: { message: 'Registration successful! Please sign in.' } });
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Typography variant="h4" component="h1" align="center" gutterBottom fontWeight={700}>
            Create Account
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 3 }}>
            Join Task Manager today
          </Typography>

          {(error || validationError) && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error || validationError}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              name="full_name"
              label="Full Name"
              fullWidth
              margin="normal"
              value={formData.full_name}
              onChange={handleChange}
            />
            <TextField
              name="email"
              label="Email"
              type="email"
              fullWidth
              margin="normal"
              value={formData.email}
              onChange={handleChange}
              required
            />
            <TextField
              name="username"
              label="Username"
              fullWidth
              margin="normal"
              value={formData.username}
              onChange={handleChange}
              required
              helperText="Letters, numbers, underscores, and hyphens only"
            />
            <TextField
              name="password"
              label="Password"
              type="password"
              fullWidth
              margin="normal"
              value={formData.password}
              onChange={handleChange}
              required
              helperText="At least 8 characters with uppercase, lowercase, and number"
            />
            <TextField
              name="confirmPassword"
              label="Confirm Password"
              type="password"
              fullWidth
              margin="normal"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
            <Button
              type="submit"
              variant="contained"
              fullWidth
              size="large"
              disabled={loading}
              sx={{ mt: 3, mb: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Create Account'}
            </Button>
          </form>

          <Typography align="center">
            Already have an account?{' '}
            <Link component={RouterLink} to="/login">
              Sign in
            </Link>
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
};

export default Register;
