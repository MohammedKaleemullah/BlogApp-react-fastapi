import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { Dialog, DialogTrigger, DialogContent, DialogTitle } from "./ui/dialog";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";

export function NewBlogDialog({ onBlogAdded }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  const handleAdd = () => {
    if (!title.trim() || !content.trim()) return;

    const newBlog = {
      id: uuidv4(),
      title,
      content,
      author: "Anonymous",
    };

    onBlogAdded?.(newBlog);
    setTitle("");
    setContent("");
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">+ Add Blog</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>New Blog</DialogTitle>
        <Input
          placeholder="Blog Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <Textarea
          placeholder="Write your blog here..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <Button onClick={handleAdd}>Post</Button>
      </DialogContent>
    </Dialog>
  );
}
