"use client";

import { Cards02Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar";

import { NavUser } from "./nav-user";

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center gap-2 px-2 py-1">
          <HugeiconsIcon
            icon={Cards02Icon}
            strokeWidth={2}
            className="h-6 w-6"
          />
          <h1 className="text-lg font-bold">Pokémon Companion</h1>
        </div>
      </SidebarHeader>

      <SidebarContent />

      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
    </Sidebar>
  );
}
