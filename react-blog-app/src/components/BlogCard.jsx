import { Link } from "react-router-dom";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui/card";

function BlogCard({ id, title, content, author }) {
  return (
    <Link to={`/blogs/${id}`} className="block">
      <Card className="shadow-md hover:shadow-xl transition duration-300 ">
        <CardHeader>
          <CardTitle className="text-lg line-clamp-1">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground line-clamp-1">{content}</p>
        </CardContent>
        <CardFooter className="text-xs text-right text-muted-foreground">
          <span>— {author}</span>
        </CardFooter>
      </Card>
    </Link>
  );
}

export default BlogCard;