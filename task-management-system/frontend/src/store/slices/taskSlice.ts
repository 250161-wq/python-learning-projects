import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export interface Task {
  id: number;
  title: string;
  description: string | null;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'todo' | 'in_progress' | 'in_review' | 'completed' | 'archived';
  category: string;
  due_date: string | null;
  owner: {
    id: number;
    username: string;
    full_name: string | null;
  };
  assignee: {
    id: number;
    username: string;
    full_name: string | null;
  } | null;
  created_at: string;
  updated_at: string;
  is_overdue: boolean;
}

interface TaskState {
  tasks: Task[];
  currentTask: Task | null;
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  error: string | null;
}

const initialState: TaskState = {
  tasks: [],
  currentTask: null,
  total: 0,
  page: 1,
  pageSize: 20,
  loading: false,
  error: null,
};

export const fetchTasks = createAsyncThunk(
  'tasks/fetchTasks',
  async (params: { page?: number; status?: string[]; priority?: string[]; query?: string } = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/tasks', { params });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch tasks');
    }
  }
);

export const fetchTask = createAsyncThunk(
  'tasks/fetchTask',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/tasks/${id}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch task');
    }
  }
);

export const createTask = createAsyncThunk(
  'tasks/createTask',
  async (taskData: Partial<Task>, { rejectWithValue }) => {
    try {
      const response = await api.post('/tasks', taskData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create task');
    }
  }
);

export const updateTask = createAsyncThunk(
  'tasks/updateTask',
  async ({ id, data }: { id: number; data: Partial<Task> }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/tasks/${id}`, data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update task');
    }
  }
);

export const deleteTask = createAsyncThunk(
  'tasks/deleteTask',
  async (id: number, { rejectWithValue }) => {
    try {
      await api.delete(`/tasks/${id}`);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete task');
    }
  }
);

const taskSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: {
    clearCurrentTask: (state) => {
      state.currentTask = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTasks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = action.payload.items;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.pageSize = action.payload.page_size;
      })
      .addCase(fetchTasks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchTask.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchTask.fulfilled, (state, action) => {
        state.loading = false;
        state.currentTask = action.payload;
      })
      .addCase(fetchTask.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(createTask.fulfilled, (state, action) => {
        state.tasks.unshift(action.payload);
        state.total += 1;
      })
      .addCase(updateTask.fulfilled, (state, action) => {
        const index = state.tasks.findIndex(t => t.id === action.payload.id);
        if (index !== -1) {
          state.tasks[index] = action.payload;
        }
        if (state.currentTask?.id === action.payload.id) {
          state.currentTask = action.payload;
        }
      })
      .addCase(deleteTask.fulfilled, (state, action) => {
        state.tasks = state.tasks.filter(t => t.id !== action.payload);
        state.total -= 1;
      });
  },
});

export const { clearCurrentTask, clearError } = taskSlice.actions;
export default taskSlice.reducer;
