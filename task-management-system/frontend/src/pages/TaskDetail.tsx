import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  IconButton,
  CircularProgress,
} from '@mui/material';
import {
  ArrowBack,
  Edit,
  Delete,
  Save,
  Cancel,
} from '@mui/icons-material';
import { RootState, AppDispatch } from '../store';
import { fetchTask, updateTask, deleteTask, clearCurrentTask } from '../store/slices/taskSlice';

const TaskDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { currentTask, loading } = useSelector((state: RootState) => state.tasks);

  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<any>({});

  useEffect(() => {
    if (id) {
      dispatch(fetchTask(parseInt(id)));
    }
    return () => {
      dispatch(clearCurrentTask());
    };
  }, [dispatch, id]);

  useEffect(() => {
    if (currentTask) {
      setEditData({
        title: currentTask.title,
        description: currentTask.description || '',
        status: currentTask.status,
        priority: currentTask.priority,
        category: currentTask.category,
      });
    }
  }, [currentTask]);

  const handleSave = async () => {
    if (currentTask) {
      await dispatch(updateTask({ id: currentTask.id, data: editData }));
      setIsEditing(false);
    }
  };

  const handleDelete = async () => {
    if (currentTask && window.confirm('Are you sure you want to delete this task?')) {
      await dispatch(deleteTask(currentTask.id));
      navigate('/tasks');
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

  if (loading || !currentTask) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <IconButton onClick={() => navigate('/tasks')}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h4" fontWeight={600} sx={{ flex: 1 }}>
          Task Details
        </Typography>
        {!isEditing ? (
          <>
            <Button
              variant="outlined"
              startIcon={<Edit />}
              onClick={() => setIsEditing(true)}
            >
              Edit
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Delete />}
              onClick={handleDelete}
            >
              Delete
            </Button>
          </>
        ) : (
          <>
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
            >
              Save
            </Button>
            <Button
              variant="outlined"
              startIcon={<Cancel />}
              onClick={() => setIsEditing(false)}
            >
              Cancel
            </Button>
          </>
        )}
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              {isEditing ? (
                <>
                  <TextField
                    fullWidth
                    label="Title"
                    value={editData.title}
                    onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                    margin="normal"
                  />
                  <TextField
                    fullWidth
                    label="Description"
                    value={editData.description}
                    onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                    margin="normal"
                    multiline
                    rows={4}
                  />
                </>
              ) : (
                <>
                  <Typography variant="h5" fontWeight={600} mb={2}>
                    {currentTask.title}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    {currentTask.description || 'No description provided'}
                  </Typography>
                </>
              )}

              <Divider sx={{ my: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  {isEditing ? (
                    <FormControl fullWidth size="small">
                      <InputLabel>Status</InputLabel>
                      <Select
                        value={editData.status}
                        label="Status"
                        onChange={(e) => setEditData({ ...editData, status: e.target.value })}
                      >
                        <MenuItem value="todo">To Do</MenuItem>
                        <MenuItem value="in_progress">In Progress</MenuItem>
                        <MenuItem value="in_review">In Review</MenuItem>
                        <MenuItem value="completed">Completed</MenuItem>
                      </Select>
                    </FormControl>
                  ) : (
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Status
                      </Typography>
                      <Box mt={0.5}>
                        <Chip
                          label={currentTask.status.replace('_', ' ')}
                          color={getStatusColor(currentTask.status) as any}
                        />
                      </Box>
                    </Box>
                  )}
                </Grid>
                <Grid item xs={6}>
                  {isEditing ? (
                    <FormControl fullWidth size="small">
                      <InputLabel>Priority</InputLabel>
                      <Select
                        value={editData.priority}
                        label="Priority"
                        onChange={(e) => setEditData({ ...editData, priority: e.target.value })}
                      >
                        <MenuItem value="low">Low</MenuItem>
                        <MenuItem value="medium">Medium</MenuItem>
                        <MenuItem value="high">High</MenuItem>
                        <MenuItem value="urgent">Urgent</MenuItem>
                      </Select>
                    </FormControl>
                  ) : (
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Priority
                      </Typography>
                      <Box mt={0.5}>
                        <Chip
                          label={currentTask.priority}
                          color={getPriorityColor(currentTask.priority) as any}
                        />
                      </Box>
                    </Box>
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} mb={2}>
                Details
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Owner
                  </Typography>
                  <Typography>{currentTask.owner?.username || 'Unknown'}</Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Assignee
                  </Typography>
                  <Typography>{currentTask.assignee?.username || 'Unassigned'}</Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Category
                  </Typography>
                  <Typography sx={{ textTransform: 'capitalize' }}>
                    {currentTask.category}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Created
                  </Typography>
                  <Typography>
                    {new Date(currentTask.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Updated
                  </Typography>
                  <Typography>
                    {new Date(currentTask.updated_at).toLocaleDateString()}
                  </Typography>
                </Box>
                {currentTask.is_overdue && (
                  <Chip label="Overdue" color="error" size="small" />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TaskDetail;
