import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import taskReducer from './slices/taskSlice';
import teamReducer from './slices/teamSlice';
import notificationReducer from './slices/notificationSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    tasks: taskReducer,
    teams: teamReducer,
    notifications: notificationReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
