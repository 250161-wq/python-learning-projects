import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  CircularProgress,
  Pagination,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  FilterList,
} from '@mui/icons-material';
import { RootState, AppDispatch } from '../store';
import { fetchTasks, createTask, deleteTask, Task } from '../store/slices/taskSlice';

const Tasks: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const dispatch = useDispatch<AppDispatch>();
  const { tasks, total, page, pageSize, loading } = useSelector((state: RootState) => state.tasks);

  const [openCreate, setOpenCreate] = useState(searchParams.get('create') === 'true');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string[]>([]);
  const [priorityFilter, setPriorityFilter] = useState<string[]>([]);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium',
    category: 'other',
  });

  useEffect(() => {
    dispatch(fetchTasks({
      query: searchQuery || undefined,
      status: statusFilter.length ? statusFilter : undefined,
      priority: priorityFilter.length ? priorityFilter : undefined,
    }));
  }, [dispatch, searchQuery, statusFilter, priorityFilter]);

  const handleCreateTask = async () => {
    if (newTask.title.trim()) {
      await dispatch(createTask(newTask));
      setOpenCreate(false);
      setNewTask({ title: '', description: '', priority: 'medium', category: 'other' });
      searchParams.delete('create');
      setSearchParams(searchParams);
    }
  };

  const handleDeleteTask = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this task?')) {
      await dispatch(deleteTask(id));
    }
  };

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

  const totalPages = Math.ceil(total / pageSize);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight={600}>
          Tasks
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenCreate(true)}
        >
          New Task
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  multiple
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as string[])}
                  label="Status"
                  renderValue={(selected) => selected.join(', ')}
                >
                  <MenuItem value="todo">To Do</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="in_review">In Review</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Priority</InputLabel>
                <Select
                  multiple
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value as string[])}
                  label="Priority"
                  renderValue={(selected) => selected.join(', ')}
                >
                  <MenuItem value="urgent">Urgent</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tasks Grid */}
      {loading ? (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Grid container spacing={2}>
            {tasks.map((task) => (
              <Grid item xs={12} sm={6} md={4} key={task.id}>
                <Card
                  sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}
                  onClick={() => navigate(`/tasks/${task.id}`)}
                >
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="start">
                      <Typography variant="h6" fontWeight={600} noWrap sx={{ flex: 1 }}>
                        {task.title}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={(e) => handleDeleteTask(task.id, e)}
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    </Box>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mb: 2,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {task.description || 'No description'}
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap">
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
                      {task.is_overdue && (
                        <Chip label="Overdue" size="small" color="error" />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {tasks.length === 0 && (
            <Box textAlign="center" py={4}>
              <Typography variant="h6" color="text.secondary">
                No tasks found
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setOpenCreate(true)}
                sx={{ mt: 2 }}
              >
                Create Your First Task
              </Button>
            </Box>
          )}

          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={3}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(_, p) => dispatch(fetchTasks({ page: p }))}
              />
            </Box>
          )}
        </>
      )}

      {/* Create Task Dialog */}
      <Dialog open={openCreate} onClose={() => setOpenCreate(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Task</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Title"
            fullWidth
            value={newTask.title}
            onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
            required
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={newTask.description}
            onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Priority</InputLabel>
            <Select
              value={newTask.priority}
              label="Priority"
              onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
            >
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="urgent">Urgent</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth margin="dense">
            <InputLabel>Category</InputLabel>
            <Select
              value={newTask.category}
              label="Category"
              onChange={(e) => setNewTask({ ...newTask, category: e.target.value })}
            >
              <MenuItem value="bug">Bug</MenuItem>
              <MenuItem value="feature">Feature</MenuItem>
              <MenuItem value="improvement">Improvement</MenuItem>
              <MenuItem value="documentation">Documentation</MenuItem>
              <MenuItem value="maintenance">Maintenance</MenuItem>
              <MenuItem value="research">Research</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreate(false)}>Cancel</Button>
          <Button onClick={handleCreateTask} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Tasks;
