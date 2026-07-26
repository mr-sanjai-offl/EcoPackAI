import { Bell, Search, User } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export function Navbar() {
  return (
    <header className="h-16 border-b bg-background flex items-center justify-between px-8 z-10 sticky top-0">
      <div className="flex items-center w-96 relative">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input 
          type="search" 
          placeholder="Search materials or predictions..." 
          className="pl-9 bg-muted/50 border-none focus-visible:ring-1"
        />
      </div>
      
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="icon" className="relative text-muted-foreground">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-primary" />
        </Button>
        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
          <User className="h-4 w-4 text-primary" />
        </div>
      </div>
    </header>
  );
}
