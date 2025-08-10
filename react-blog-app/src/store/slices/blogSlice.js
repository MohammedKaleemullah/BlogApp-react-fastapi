import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

// Fetch all blogs
export const fetchBlogs = createAsyncThunk(
  "blogs/fetchBlogs",
  async ({ offset, limit, visibility }) => {
    const res = await fetch(
      `${API_BASE}/blogs?limit=${limit}&offset=${offset}&visibility=${visibility}`
    );
    return await res.json();
  }
);

// Fetch single blog
export const fetchBlogById = createAsyncThunk(
  "blogs/fetchBlogById",
  async (id, { rejectWithValue }) => {
    try {
      const res = await axios.get(`${API_BASE}/blogs/${id}`);
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
    blogDetails: null,
    total: 0,
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
      state.total = 0;
    },
    clearBlogDetails: (state) => {
      state.blogDetails = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchBlogs.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchBlogs.fulfilled, (state, action) => {
        state.loading = false;
        const newItems = Array.isArray(action.payload) ? action.payload : [];

        // ✅ Filter out duplicates by ID
        const existingIds = new Set(state.items.map((b) => b.id));
        const uniqueItems = newItems.filter((b) => !existingIds.has(b.id));

        state.items = [...state.items, ...uniqueItems];
        state.hasMore = newItems.length > 0;
        if (uniqueItems.length > 0) {
          state.offset += state.limit;
        }
      })
      .addCase(fetchBlogs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(fetchBlogById.pending, (state) => {
        state.loading = true;
        state.blogDetails = null;
      })
      .addCase(fetchBlogById.fulfilled, (state, action) => {
        state.loading = false;
        state.blogDetails = action.payload;
      })
      .addCase(fetchBlogById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { resetBlogs, clearBlogDetails } = blogSlice.actions;
export default blogSlice.reducer;
