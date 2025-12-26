import React from 'react';
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ILauncher } from '@jupyterlab/launcher';
import { ReactWidget } from '@jupyterlab/apputils';
import { PageConfig } from '@jupyterlab/coreutils';
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Stack,
  Typography
} from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import useSWR from 'swr';

const PLUGIN_ID = 'jupyterlab-paperspace-model-cockpit:plugin';
const COMMAND_ID = 'paperspace-model-cockpit:open';

class CockpitWidget extends ReactWidget {
  constructor() {
    super();
    this.addClass('jp-PaperspaceModelCockpit');
  }

  render(): JSX.Element {
    const theme = createTheme();
    const baseUrl = PageConfig.getBaseUrl();
    const endpoint = `${baseUrl}paperspace-model-cockpit/api/models`;
    const fetcher = (url: string) =>
      fetch(url, { credentials: 'same-origin' }).then(res => {
        if (!res.ok) {
          throw new Error(`Request failed: ${res.status}`);
        }
        return res.json();
      });
    const { data, error, isLoading } = useSWR(endpoint, fetcher);
    const models = Array.isArray(data?.models) ? data.models : [];

    return (
      <ThemeProvider theme={theme}>
        <Box sx={{ p: 3, height: '100%' }}>
          <Stack spacing={2}>
            <Typography variant="h5">Paperspace Model Cockpit</Typography>
            <Typography variant="body2">
              models.json based model list. Auto-install happens on server start.
            </Typography>
            {isLoading && (
              <Stack direction="row" spacing={1} alignItems="center">
                <CircularProgress size={18} />
                <Typography variant="body2">Loading models...</Typography>
              </Stack>
            )}
            {error && <Alert severity="error">Failed to load models list.</Alert>}
            {!isLoading && !error && (
              <List dense>
                {models.length === 0 && (
                  <ListItem>
                    <ListItemText primary="No models defined in models.json." />
                  </ListItem>
                )}
                {models.map((model: any) => (
                  <ListItem key={model.id} divider>
                    <ListItemText
                      primary={`${model.display_name ?? model.id} (${model.version ?? '-'})`}
                      secondary={model.path ?? ''}
                    />
                    <Chip
                      label={model.installed ? 'installed' : 'not installed'}
                      color={model.installed ? 'success' : 'default'}
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Stack>
        </Box>
      </ThemeProvider>
    );
  }
}

const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  requires: [ILauncher],
  activate: (app: JupyterFrontEnd, launcher: ILauncher) => {
    const { commands, shell } = app;

    commands.addCommand(COMMAND_ID, {
      label: 'Paperspace Model Cockpit',
      execute: () => {
        const widget = new CockpitWidget();
        widget.id = 'paperspace-model-cockpit';
        widget.title.label = 'Model Cockpit';
        widget.title.closable = true;
        shell.add(widget, 'main');
      }
    });

    launcher.add({
      command: COMMAND_ID,
      category: 'Paperspace',
      rank: 1
    });
  }
};

export default plugin;
