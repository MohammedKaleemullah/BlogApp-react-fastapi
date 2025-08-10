import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const fetchBlogs = createAsyncThunk(
  "blogs/fetchBlogs",
  async ({ offset = 0, limit = 10, tags, visibility }, { rejectWithValue }) => {
    try {
      const params = { limit, offset };
      if (tags) params.tags = tags;
      if (visibility) params.visibility = visibility;

      const res = await axios.get(`${API_BASE}/blogs`, { params });
      // Backend returns an array directly
      return res.data;
    } catch (err) {
      return rejectWithValue(err.response?.data || err.message);
    }
  }
);

const blogSlice = createSlice({
  name: "blogs",
  initialState: {
    items: [],
    offset: 0,
    limit: 10,
    hasMore: true,
    loading: false,
    error: null,
  },
  reducers: {
    resetBlogs: (state) => {
      state.items = [];
      state.offset = 0;
      state.hasMore = true;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchBlogs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBlogs.fulfilled, (state, action) => {
        state.loading = false;

        const newItems = Array.isArray(action.payload) ? action.payload : [];

        // Filter out duplicates based on blog ID
        const uniqueNewItems = newItems.filter(
          (blog) => !state.items.some((b) => b.id === blog.id)
        );

        state.items = [...state.items, ...uniqueNewItems];
        state.hasMore = uniqueNewItems.length > 0;
        state.offset += state.limit; // increment offset for next request
      })
      .addCase(fetchBlogs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || "Failed to fetch blogs";
      });
  },
});

export const { resetBlogs } = blogSlice.actions;
export default blogSlice.reducer;
