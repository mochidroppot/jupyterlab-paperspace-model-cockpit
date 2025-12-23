import React from 'react';
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ILauncher } from '@jupyterlab/launcher';
import { ReactWidget } from '@jupyterlab/apputils';
import { Box, Button, Stack, Typography } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const PLUGIN_ID = 'jupyterlab-paperspace-model-cockpit:plugin';
const COMMAND_ID = 'paperspace-model-cockpit:open';

class CockpitWidget extends ReactWidget {
  constructor() {
    super();
    this.addClass('jp-PaperspaceModelCockpit');
  }

  render(): JSX.Element {
    const theme = createTheme();

    return (
      <ThemeProvider theme={theme}>
        <Box sx={{ p: 3, height: '100%' }}>
          <Stack spacing={2}>
            <Typography variant="h5">Paperspace Model Cockpit</Typography>
            <Typography variant="body2">
              UI placeholder. Server handles models.json and auto-install checks on startup.
            </Typography>
            <Button variant="contained" disabled>
              Install Selected (stub)
            </Button>
          </Stack>
        </Box>
      </ThemeProvider>
    );
  }
}

const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  optional: [ILauncher],
  activate: (app: JupyterFrontEnd, launcher: ILauncher | null) => {
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

    if (launcher) {
      launcher.add({
        command: COMMAND_ID,
        category: 'Paperspace'
      });
    }
  }
};

export default plugin;
