<script>
  import "../app.pcss";
  import { AppShell } from '@skeletonlabs/skeleton';
  import { AppBar } from '@skeletonlabs/skeleton';

  
  </script>

<AppShell slotSidebarLeft="bg-surface-500/5 w-56 p-4">
    <svelte:fragment slot="header">
        <AppBar gridColumns="grid-cols-3" slotDefault="place-self-center" slotTrail="place-content-end">
            <svelte:fragment slot="lead">(icon)</svelte:fragment>
            (title)
            <svelte:fragment slot="trail">(actions)</svelte:fragment>
        </AppBar>
    	</svelte:fragment>
    <svelte:fragment slot="sidebarLeft">
        <!-- Insert the list: -->
        <nav class="list-nav">
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
            </ul>
        </nav>
        <!-- --- -->
    </svelte:fragment>

    <slot />
</AppShell>