"use client";

import {
  Sidebar,
  SidebarFooter,
  SidebarHeader
} from "@/components/ui/sidebar";
import { Cards02Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import { usePathname } from "next/navigation";

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center gap-2 px-2 py-1">
          <HugeiconsIcon
            icon={Cards02Icon}
            strokeWidth={2}
            className="w-6 h-6"
          />
          <h1 className="text-lg font-bold">Pokémon Companion</h1>
        </div>
      </SidebarHeader>

      <SidebarFooter>
        <div className="px-2 py-1 text-xs text-muted-foreground text-center">
          v0.1.0 Beta
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
