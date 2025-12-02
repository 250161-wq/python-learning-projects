import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
} from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import api from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Analytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await api.get('/analytics/tasks');
        setAnalytics(response.data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  const statusData = {
    labels: analytics?.status_breakdown?.map((s: any) => s.status.replace('_', ' ')) || [],
    datasets: [
      {
        data: analytics?.status_breakdown?.map((s: any) => s.count) || [],
        backgroundColor: [
          '#2196f3',
          '#ff9800',
          '#9c27b0',
          '#4caf50',
          '#607d8b',
        ],
      },
    ],
  };

  const priorityData = {
    labels: analytics?.priority_breakdown?.map((p: any) => p.priority) || [],
    datasets: [
      {
        label: 'Tasks',
        data: analytics?.priority_breakdown?.map((p: any) => p.count) || [],
        backgroundColor: [
          '#4caf50',
          '#2196f3',
          '#ff9800',
          '#f44336',
        ],
      },
    ],
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} mb={3}>
        Analytics Dashboard
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" fontWeight={700} color="primary">
                {analytics?.total_tasks || 0}
              </Typography>
              <Typography color="text.secondary">Total Tasks</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" fontWeight={700} color="success.main">
                {analytics?.completed_tasks || 0}
              </Typography>
              <Typography color="text.secondary">Completed</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" fontWeight={700} color="warning.main">
                {analytics?.in_progress_tasks || 0}
              </Typography>
              <Typography color="text.secondary">In Progress</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h4" fontWeight={700} color="error.main">
                {analytics?.overdue_tasks || 0}
              </Typography>
              <Typography color="text.secondary">Overdue</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Completion Rate */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} mb={2}>
                Completion Rate
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                <CircularProgress
                  variant="determinate"
                  value={analytics?.completion_rate || 0}
                  size={80}
                  thickness={8}
                />
                <Typography variant="h3" fontWeight={700}>
                  {analytics?.completion_rate?.toFixed(1) || 0}%
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} mb={2}>
                Tasks by Status
              </Typography>
              <Box height={300}>
                <Pie
                  data={statusData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom',
                      },
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} mb={2}>
                Tasks by Priority
              </Typography>
              <Box height={300}>
                <Bar
                  data={priorityData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
