package dev.ftb.mods.ftbic.block.entity;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.FTBICBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.entity.FurnaceBlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public class IronFurnaceBlockEntity extends FurnaceBlockEntity {
   public IronFurnaceBlockEntity(BlockPos pos, BlockState state) {
      super(pos, state);
   }

   public BlockEntityType<?> m_58903_() {
      return FTBICBlockEntities.IRON_FURNACE.get();
   }

   protected Component m_6820_() {
      return new TranslatableComponent(((Block)FTBICBlocks.IRON_FURNACE.get()).m_7705_());
   }

   protected int m_7743_(ItemStack stack) {
      return Math.round((float)super.m_7743_(stack) * (float)((Integer)FTBICConfig.MACHINES.IRON_FURNACE_ITEMS_PER_COAL.get()).intValue() / 8.0F);
   }
}
