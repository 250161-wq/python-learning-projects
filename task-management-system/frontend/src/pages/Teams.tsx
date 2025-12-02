import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Chip,
  CircularProgress,
} from '@mui/material';
import { Add, Group, Person } from '@mui/icons-material';
import { RootState, AppDispatch } from '../store';
import { fetchTeams, createTeam } from '../store/slices/teamSlice';

const Teams: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { teams, loading } = useSelector((state: RootState) => state.teams);

  const [openCreate, setOpenCreate] = useState(false);
  const [newTeam, setNewTeam] = useState({ name: '', description: '' });

  useEffect(() => {
    dispatch(fetchTeams());
  }, [dispatch]);

  const handleCreateTeam = async () => {
    if (newTeam.name.trim()) {
      await dispatch(createTeam(newTeam));
      setOpenCreate(false);
      setNewTeam({ name: '', description: '' });
    }
  };

  if (loading && teams.length === 0) {
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
          Teams
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenCreate(true)}
        >
          Create Team
        </Button>
      </Box>

      <Grid container spacing={3}>
        {teams.map((team) => (
          <Grid item xs={12} sm={6} md={4} key={team.id}>
            <Card sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    <Group />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" fontWeight={600}>
                      {team.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {team.description || 'No description'}
                    </Typography>
                  </Box>
                </Box>
                <Box display="flex" gap={1}>
                  <Chip
                    icon={<Person />}
                    label={`${team.members_count} members`}
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    label={`${team.tasks_count} tasks`}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}

        {teams.length === 0 && (
          <Grid item xs={12}>
            <Box textAlign="center" py={4}>
              <Typography variant="h6" color="text.secondary">
                No teams yet
              </Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setOpenCreate(true)}
                sx={{ mt: 2 }}
              >
                Create Your First Team
              </Button>
            </Box>
          </Grid>
        )}
      </Grid>

      {/* Create Team Dialog */}
      <Dialog open={openCreate} onClose={() => setOpenCreate(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Team</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Team Name"
            fullWidth
            value={newTeam.name}
            onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })}
            required
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            value={newTeam.description}
            onChange={(e) => setNewTeam({ ...newTeam, description: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreate(false)}>Cancel</Button>
          <Button onClick={handleCreateTeam} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Teams;
