
import click

from .config import Config
from .sync import SyncEngine
from .git_handler import GitHandler


@click.group()
@click.version_option()
def main():
    pass


@main.command()
@click.option("--no-push", is_flag=True, help="Sync files but don't push to GitHub")
@click.option("--message", "-m", help="Custom commit message")
def sync(no_push, message):
    """Sync Obsidian vault to GitHub repository."""
    try:
        cfg = Config.from_file("config.yaml")
        
        click.echo(f"📂 Vault: {cfg.vault_path}")
        click.echo(f"📤 Output: {cfg.output_path}")
        click.echo()
        
        if not cfg.vault_path.exists():
            raise click.ClickException(f"Vault not found: {cfg.vault_path}")
        
        engine = SyncEngine(cfg)
        stats = engine.sync()
        
        click.echo(f"✅ Synced {stats['files']} files")
        click.echo(f"🖼️  Copied {stats['images']} images")
        if stats['skipped'] > 0:
            click.echo(f"⏭️  Skipped {stats['skipped']} unchanged files")
        
        # Push if requested
        if not no_push and stats['files'] > 0:
            click.echo()
            click.echo("📤 Pushing to GitHub...")
            
            git = GitHandler(cfg.output_path)
            if git.commit_and_push(message):
                click.echo("✅ Pushed successfully!")
            else:
                click.echo("ℹ️  Nothing to push")
        
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Sync failed: {e}")


@main.command()
@click.option("--param", "-p", help="Test param")
def check(param):
    """Test command."""
    click.echo(param)


@main.command()
def status():
    """Show current sync status."""
    try:
        cfg = Config.from_file("config.yaml")
        
        click.echo(f"📂 Vault: {cfg.vault_path}")
        click.echo(f"   Exists: {'✅' if cfg.vault_path.exists() else '❌'}")
        
        click.echo(f"📤 Output: {cfg.output_path}")
        click.echo(f"   Exists: {'✅' if cfg.output_path.exists() else '❌'}")
        
        if cfg.output_path.exists():
            try:
                git = GitHandler(cfg.output_path)
                git_status = git.status()
                click.echo(f"   Branch: {git_status['branch']}")
                click.echo(f"   Uncommitted: {'Yes' if git_status['dirty'] else 'No'}")
                click.echo(f"   Untracked: {git_status['untracked']}")
            except ValueError:
                click.echo("   Git: Not initialized")
        
        click.echo(f"🌐 GitHub: {cfg.github.username}/{cfg.github.repo}")
        
    except FileNotFoundError as e:
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main()
