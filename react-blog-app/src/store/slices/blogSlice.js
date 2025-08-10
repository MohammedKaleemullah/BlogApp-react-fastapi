import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

export const fetchBlogs = createAsyncThunk('blogs/fetch', async ({ limit=10, offset=0, tags, visibility='public' } = {}, { rejectWithValue }) => {
  try {
    const params = { limit, offset, visibility }
    if (tags) params.tags = tags
    const res = await api.get('/blogs', { params })
    return res.data
  } catch (err) {
    return rejectWithValue(err.response?.data || err.message)
  }
})

const blogSlice = createSlice({
  name: 'blogs',
  initialState: { items: [], loading: false, error: null, hasMore: true },
  reducers: {
    clearBlogs(state){ state.items = []; state.hasMore = true }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchBlogs.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchBlogs.fulfilled, (state, action) => {
        state.loading = false
        if (!action.payload || action.payload.length === 0) state.hasMore = false
        state.items = [...state.items, ...action.payload]
      })
      .addCase(fetchBlogs.rejected, (state, action) => {
        state.loading = false; state.error = action.payload
      })
  }
})

export const { clearBlogs } = blogSlice.actions
export default blogSlice.reducer
