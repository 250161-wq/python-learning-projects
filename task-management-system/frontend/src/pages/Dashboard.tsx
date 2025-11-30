import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  Assignment,
  CheckCircle,
  Warning,
  TrendingUp,
  Add,
} from '@mui/icons-material';
import { RootState, AppDispatch } from '../store';
import { fetchTasks, Task } from '../store/slices/taskSlice';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { tasks, loading } = useSelector((state: RootState) => state.tasks);
  const { user } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    dispatch(fetchTasks({}));
  }, [dispatch]);

  const stats = {
    total: tasks.length,
    completed: tasks.filter((t) => t.status === 'completed').length,
    inProgress: tasks.filter((t) => t.status === 'in_progress').length,
    overdue: tasks.filter((t) => t.is_overdue).length,
  };

  const recentTasks = tasks.slice(0, 5);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'primary';
      case 'in_review': return 'secondary';
      default: return 'default';
    }
  };

  if (loading && tasks.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight={600}>
          Welcome back, {user?.full_name || user?.username}!
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => navigate('/tasks?create=true')}
        >
          New Task
        </Button>
      </Box>

      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Assignment color="primary" sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" fontWeight={700}>{stats.total}</Typography>
                  <Typography color="text.secondary">Total Tasks</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" fontWeight={700}>{stats.completed}</Typography>
                  <Typography color="text.secondary">Completed</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <TrendingUp color="info" sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" fontWeight={700}>{stats.inProgress}</Typography>
                  <Typography color="text.secondary">In Progress</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Warning color="error" sx={{ fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" fontWeight={700}>{stats.overdue}</Typography>
                  <Typography color="text.secondary">Overdue</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} mb={2}>
                Recent Tasks
              </Typography>
              <List>
                {recentTasks.map((task, index) => (
                  <React.Fragment key={task.id}>
                    {index > 0 && <Divider />}
                    <ListItem
                      sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}
                      onClick={() => navigate(`/tasks/${task.id}`)}
                    >
                      <ListItemText
                        primary={task.title}
                        secondary={task.description?.substring(0, 100) || 'No description'}
                      />
                      <Box display="flex" gap={1}>
                        <Chip
                          label={task.priority}
                          size="small"
                          color={getPriorityColor(task.priority) as any}
                        />
                        <Chip
                          label={task.status.replace('_', ' ')}
                          size="small"
                          color={getStatusColor(task.status) as any}
                          variant="outlined"
                        />
                      </Box>
                    </ListItem>
                  </React.Fragment>
                ))}
                {recentTasks.length === 0 && (
                  <ListItem>
                    <ListItemText
                      primary="No tasks yet"
                      secondary="Create your first task to get started"
                    />
                  </ListItem>
                )}
              </List>
              {tasks.length > 5 && (
                <Button onClick={() => navigate('/tasks')} sx={{ mt: 2 }}>
                  View All Tasks
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} mb={2}>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate('/tasks?create=true')}
                >
                  Create New Task
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate('/teams')}
                >
                  Manage Teams
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate('/analytics')}
                >
                  View Analytics
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
