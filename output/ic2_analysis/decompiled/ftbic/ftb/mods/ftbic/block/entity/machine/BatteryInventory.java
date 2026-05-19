package dev.ftb.mods.ftbic.block.entity.machine;

import dev.ftb.mods.ftbic.block.entity.ElectricBlockEntity;
import dev.ftb.mods.ftbic.util.EnergyItemHandler;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.items.ItemStackHandler;
import org.jetbrains.annotations.NotNull;

public class BatteryInventory extends ItemStackHandler {
   public final ElectricBlockEntity entity;
   public final boolean charge;

   public BatteryInventory(ElectricBlockEntity e, boolean c) {
      super(1);
      this.entity = e;
      this.charge = c;
   }

   public void loadItem(ItemStack stack) {
      this.stacks.set(0, stack);
   }

   protected void onContentsChanged(int slot) {
      this.entity.m_6596_();
   }

   public boolean isItemValid(int slot, @NotNull ItemStack stack) {
      return stack.m_41720_() instanceof EnergyItemHandler
         && (this.charge ? ((EnergyItemHandler)stack.m_41720_()).canInsertEnergy() : ((EnergyItemHandler)stack.m_41720_()).canExtractEnergy());
   }

   public int getSlotLimit(int slot) {
      return 1;
   }
}
