import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { NAV_ITEMS } from '@/lib/constants';
import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

// Import all Lucide icons
import * as LucideIcons from 'lucide-react';

const Sidebar = ({ className }) => {
  const location = useLocation();
  
  return (
    <div className={cn(
      "flex h-screen w-64 flex-col border-r bg-sidebar text-sidebar-foreground",
      className
    )}>
      <div className="flex h-14 items-center border-b px-4">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <LucideIcons.BarChart2 className="h-6 w-6 text-sidebar-primary" />
          <span className="text-xl">Financial Portal</span>
        </Link>
      </div>
      
      <nav className="flex-1 overflow-auto p-4">
        <ul className="space-y-2">
          {NAV_ITEMS.map((item) => {
            // Dynamically get the icon component
            const IconComponent = LucideIcons[item.icon.charAt(0).toUpperCase() + item.icon.slice(1)];
            
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    location.pathname === item.path
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
                  )}
                >
                  {IconComponent && <IconComponent className="h-5 w-5" />}
                  <span>{item.title}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      
      <div className="border-t p-4">
        <div className="flex items-center gap-3 rounded-md px-3 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-sidebar-primary text-sidebar-primary-foreground">
            <LucideIcons.User className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-medium">Guest User</p>
            <p className="text-xs text-sidebar-foreground/70">guest@example.com</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;

