<template>
  <LandingPage v-if="route.name === 'landing'" />
  <WorkspaceLayout v-else :section="route.section">
    <KeepAlive>
      <component :is="views[route.section]" />
    </KeepAlive>
  </WorkspaceLayout>
</template>

<script setup lang="ts">
import { route } from '@/router';
import LandingPage from '@/views/LandingPage.vue';
import WorkspaceLayout from '@/views/WorkspaceLayout.vue';
import ConverterView from '@/views/ConverterView.vue';
import BatchView from '@/views/BatchView.vue';
import HistoryView from '@/views/HistoryView.vue';
import GuidesView from '@/views/GuidesView.vue';

const views = {
  convert: ConverterView,
  batch: BatchView,
  history: HistoryView,
  guides: GuidesView,
};
</script>
