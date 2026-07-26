import Link from 'next/link';
import { Package, LayoutDashboard, History, BarChart3, FileText, Settings } from 'lucide-react';

export function Sidebar() {
  const routes = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Recommend', path: '/recommend', icon: Package },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'History', path: '/history', icon: History },
    { name: 'Reports', path: '/reports', icon: FileText },
  ];

  return (
    <aside className="w-64 border-r bg-card min-h-screen flex flex-col">
      <div className="h-16 flex items-center px-6 border-b">
        <Package className="h-6 w-6 text-primary mr-2" />
        <span className="font-bold text-lg tracking-tight">EcoPackAI</span>
      </div>
      
      <div className="flex-1 py-6 px-4 space-y-1 overflow-y-auto">
        <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 px-2">
          Menu
        </div>
        {routes.map((route) => {
          const Icon = route.icon;
          return (
            <Link 
              key={route.path} 
              href={route.path}
              className="flex items-center px-3 py-2.5 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground transition-colors group"
            >
              <Icon className="mr-3 h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
              {route.name}
            </Link>
          )
        })}
      </div>

      <div className="p-4 border-t">
        <Link 
          href="/settings"
          className="flex items-center px-3 py-2.5 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground transition-colors group"
        >
          <Settings className="mr-3 h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
          Settings
        </Link>
      </div>
    </aside>
  );
}
