package pl.pawel.minecraftkonwersja.placeholders.world;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.TextComponent;
import net.minecraft.world.Container;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import pl.pawel.minecraftkonwersja.placeholders.registry.ModBlockEntities;

public class InventoryPlaceholderBlockEntity extends BlockEntityPlaceholderBlockEntity implements MenuProvider {
    private static final int SIZE = 54;
    private final SimpleContainer inventory = new SimpleContainer(SIZE) {
        @Override
        public void setChanged() {
            super.setChanged();
            InventoryPlaceholderBlockEntity.this.setChanged();
        }
    };

    public InventoryPlaceholderBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.INVENTORY_PLACEHOLDER.get(), pos, state);
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.put("attached_items", saveAttachedItems());
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        inventory.clearContent();
        if (tag.contains("attached_items", Tag.TAG_LIST)) {
            loadAttachedItems(tag.getList("attached_items", Tag.TAG_COMPOUND));
        }
    }

    @Override
    public Component getDisplayName() {
        return new TextComponent("Recovered conversion items");
    }

    @Override
    public AbstractContainerMenu createMenu(int containerId, Inventory playerInventory, Player player) {
        return ChestMenu.sixRows(containerId, playerInventory, inventory);
    }

    public int getRecoveredItemCount() {
        int count = 0;
        for (int slot = 0; slot < inventory.getContainerSize(); slot++) {
            if (!inventory.getItem(slot).isEmpty()) {
                count++;
            }
        }
        return count;
    }

    public Container getInventory() {
        return inventory;
    }

    private ListTag saveAttachedItems() {
        net.minecraft.core.NonNullList<ItemStack> items = net.minecraft.core.NonNullList.withSize(SIZE, ItemStack.EMPTY);
        for (int slot = 0; slot < SIZE; slot++) {
            items.set(slot, inventory.getItem(slot));
        }
        CompoundTag wrapper = new CompoundTag();
        ContainerHelper.saveAllItems(wrapper, items, false);
        return wrapper.getList("Items", Tag.TAG_COMPOUND);
    }

    private void loadAttachedItems(ListTag list) {
        net.minecraft.core.NonNullList<ItemStack> items = net.minecraft.core.NonNullList.withSize(SIZE, ItemStack.EMPTY);
        CompoundTag wrapper = new CompoundTag();
        wrapper.put("Items", list.copy());
        ContainerHelper.loadAllItems(wrapper, items);
        for (int slot = 0; slot < SIZE; slot++) {
            inventory.setItem(slot, items.get(slot));
        }
    }
}
