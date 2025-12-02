import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Avatar,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import { AccountCircle, Save } from '@mui/icons-material';
import { RootState, AppDispatch } from '../store';
import { fetchCurrentUser } from '../store/slices/authSlice';
import api from '../services/api';

const Profile: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { user, loading } = useSelector((state: RootState) => state.auth);

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    bio: '',
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        email: user.email || '',
        bio: '',
      });
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      await api.patch('/users/me', formData);
      dispatch(fetchCurrentUser());
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to update profile' });
    } finally {
      setSaving(false);
    }
  };

  if (loading && !user) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box maxWidth={600} mx="auto">
      <Typography variant="h4" fontWeight={600} mb={3}>
        Profile Settings
      </Typography>

      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={3}>
            <Avatar sx={{ width: 80, height: 80, bgcolor: 'primary.main', fontSize: 32 }}>
              {user?.username?.charAt(0).toUpperCase() || <AccountCircle />}
            </Avatar>
            <Box>
              <Typography variant="h5" fontWeight={600}>
                {user?.full_name || user?.username}
              </Typography>
              <Typography color="text.secondary">@{user?.username}</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                {user?.role}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 3 }} />

          {message && (
            <Alert severity={message.type} sx={{ mb: 2 }}>
              {message.text}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              label="Full Name"
              fullWidth
              margin="normal"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            />
            <TextField
              label="Email"
              type="email"
              fullWidth
              margin="normal"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
            <TextField
              label="Bio"
              fullWidth
              margin="normal"
              multiline
              rows={3}
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
            />

            <Box mt={3}>
              <Button
                type="submit"
                variant="contained"
                startIcon={saving ? <CircularProgress size={20} /> : <Save />}
                disabled={saving}
              >
                Save Changes
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Profile;
