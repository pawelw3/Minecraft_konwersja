package com.maciej916.indreb.common.block.impl.machines.compressor;

import com.maciej916.indreb.common.config.ServerConfig;
import com.maciej916.indreb.common.entity.block.BlockEntityStandardMachine;
import com.maciej916.indreb.common.recipe.impl.CompressingRecipe;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import com.maciej916.indreb.common.registries.ModRecipeType;
import com.maciej916.indreb.common.registries.ModSounds;
import java.util.Optional;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.block.state.BlockState;

public class BlockEntityCompressor extends BlockEntityStandardMachine {
   public BlockEntityCompressor(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.COMPRESSOR, pWorldPosition, pBlockState, (Integer)ServerConfig.compressor_energy_capacity.get());
   }

   @Override
   protected Optional<CompressingRecipe> getRecipe(ItemStack input) {
      return this.f_58857_.m_7465_().m_44015_((RecipeType)ModRecipeType.COMPRESSING.get(), new SimpleContainer(new ItemStack[]{input}), this.f_58857_);
   }

   @Override
   public SoundEvent getSoundEvent() {
      return ModSounds.COMPRESSOR;
   }
}
