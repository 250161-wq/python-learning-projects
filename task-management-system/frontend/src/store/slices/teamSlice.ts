import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

interface TeamMember {
  id: number;
  user_id: number;
  username: string;
  full_name: string | null;
  role: string;
  joined_at: string;
}

interface Team {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  members_count: number;
  tasks_count: number;
  members?: TeamMember[];
}

interface TeamState {
  teams: Team[];
  currentTeam: Team | null;
  total: number;
  loading: boolean;
  error: string | null;
}

const initialState: TeamState = {
  teams: [],
  currentTeam: null,
  total: 0,
  loading: false,
  error: null,
};

export const fetchTeams = createAsyncThunk(
  'teams/fetchTeams',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/teams');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch teams');
    }
  }
);

export const fetchTeam = createAsyncThunk(
  'teams/fetchTeam',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/teams/${id}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch team');
    }
  }
);

export const createTeam = createAsyncThunk(
  'teams/createTeam',
  async (teamData: { name: string; description?: string }, { rejectWithValue }) => {
    try {
      const response = await api.post('/teams', teamData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create team');
    }
  }
);

const teamSlice = createSlice({
  name: 'teams',
  initialState,
  reducers: {
    clearCurrentTeam: (state) => {
      state.currentTeam = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTeams.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTeams.fulfilled, (state, action) => {
        state.loading = false;
        state.teams = action.payload.items;
        state.total = action.payload.total;
      })
      .addCase(fetchTeams.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchTeam.fulfilled, (state, action) => {
        state.currentTeam = action.payload;
      })
      .addCase(createTeam.fulfilled, (state, action) => {
        state.teams.push(action.payload);
        state.total += 1;
      });
  },
});

export const { clearCurrentTeam } = teamSlice.actions;
export default teamSlice.reducer;
